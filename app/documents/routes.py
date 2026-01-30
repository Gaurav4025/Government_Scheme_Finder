from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
import os
import uuid

from app.auth.deps import auth
from app.db.mongo import documents_col, profiles_col
from app.documents.ocr import extract_text
from app.documents.parser import parse_12th_marksheet

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}


@router.post("/api/upload-document")
async def upload_doc(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    user=Depends(auth),
):
    """
    Upload a document, run OCR, parse structured data (if supported),
    store document metadata, and auto-update user profile.
    """

    user_id = user["user_id"]
    print(f"\n{'='*80}")
    print(f"UPLOAD STARTED - User: {user_id}, Doc Type: {doc_type}")
    print(f"{'='*80}")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG files are allowed for OCR",
        )
    user_dir = os.path.join("storage", user_id)
    os.makedirs(user_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join("storage", user_id, filename)

    with open(path, "wb") as f:
        f.write(await file.read())

    print(f"File saved to: {path}")
    try:
        extracted_text = extract_text(path)
        print(f"\n{'='*80}")
        print(f"OCR EXTRACTED TEXT ({len(extracted_text)} chars):")
        print(f"{'='*80}")
        print(extracted_text[:500])
        print(f"{'='*80}\n")
    except Exception as e:
        print(f" OCR FAILED: {e}")
        import traceback
        traceback.print_exc()
        extracted_text = ""
    parsed_data = {}


           # FIXED: Accept both "marksheet" and "12th_marksheet"
    is_marksheet = doc_type.lower() in ["12th_marksheet", "marksheet", "12th marksheet"]
    
    print(f"DEBUG: doc_type='{doc_type}', is_marksheet={is_marksheet}")
    
    # Parse if it's a 12th marksheet
    if is_marksheet and extracted_text:
        try:
            parsed_data = parse_12th_marksheet(extracted_text)
            print(f"\n{'='*80}")
            print(f"PARSED MARKSHEET DATA:")
            print(f"{'='*80}")
            print(f"Board: {parsed_data.get('board')}")
            print(f"Year: {parsed_data.get('year')}")
            print(f"Percentage: {parsed_data.get('percentage')}")
            print(f"Result: {parsed_data.get('result')}")
            print(f"Full parsed data: {parsed_data}")
            print(f"{'='*80}\n")
        except Exception as e:
            print(f"❌ PARSING FAILED: {e}")
            import traceback
            traceback.print_exc()
            parsed_data = {}
    else:
        print(f"⚠️ Skipping parsing: is_marksheet={is_marksheet}, has_text={bool(extracted_text)}")
    
    # Store document in documents collection
    doc = {
        "user_id": user_id,
        "doc_type": doc_type,
        "filename": filename,
        "path": path,
        "extracted_text": extracted_text,
        "parsed_data": parsed_data,
    }

    res = await documents_col.insert_one(doc)
    doc_id = str(res.inserted_id)

    print(f" Document saved to MongoDB with ID: {doc_id}")

    # Add document reference to profile
    await profiles_col.update_one(
        {"user_id": user_id},
        {
            "$push": {
                "documents": {
                    "doc_id": doc_id,
                    "doc_type": doc_type,
                }
            }
        },
        upsert=True,
    )
    print(f"✅ Document reference added to profile")

    # Update profile with parsed marksheet data
    if is_marksheet and parsed_data.get("percentage"):
        print(f"\n{'='*80}")
        print(f"UPDATING PROFILE WITH MARKSHEET DATA")
        print(f"{'='*80}")
        
        update_result = await profiles_col.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "marks_12": parsed_data.get("percentage"),
                    "board_12": parsed_data.get("board"),
                    "year_12": parsed_data.get("year"),
                    "result_12": parsed_data.get("result"),
                }
            },
            upsert=True,
        )
        
        print(f"✅ Profile updated - Matched: {update_result.matched_count}, Modified: {update_result.modified_count}")
        
        # Verify the update
        updated_profile = await profiles_col.find_one({"user_id": user_id})
        print(f"\n{'='*80}")
        print(f"VERIFIED PROFILE DATA IN MONGODB:")
        print(f"{'='*80}")
        if updated_profile:
            print(f"Name: {updated_profile.get('name')}")
            print(f"State: {updated_profile.get('state')}")
            print(f"Board 12: {updated_profile.get('board_12')}")
            print(f"Marks 12: {updated_profile.get('marks_12')}")
            print(f"Year 12: {updated_profile.get('year_12')}")
            print(f"Result 12: {updated_profile.get('result_12')}")
        else:
            print(" PROFILE NOT FOUND IN MONGODB!")
        print(f"{'='*80}\n")
    else:
        print(f" Not updating profile: is_marksheet={is_marksheet}, has_percentage={bool(parsed_data.get('percentage'))}")
    
    print(f"\n{'='*80}")
    print(f"UPLOAD COMPLETE")
    print(f"{'='*80}\n")

    return {
        "ok": True,
        "doc_id": doc_id,
        "parsed_data": parsed_data,
        "extracted_preview": extracted_text[:300],
    }
