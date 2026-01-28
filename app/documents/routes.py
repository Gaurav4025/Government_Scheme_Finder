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

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG files are allowed for OCR",
        )
    user_dir = os.path.join("storage", user_id)
    os.makedirs(user_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}{ext}"
    path = os.path.join(user_dir, filename)

    with open(path, "wb") as f:
        f.write(await file.read())


    try:
        extracted_text = extract_text(path)
    except Exception as e:
        print("OCR failed:", e)
        extracted_text = ""
    parsed_data = {}

    if doc_type == "12th_marksheet" and extracted_text:
        try:
            parsed_data = parse_12th_marksheet(extracted_text)
        except Exception as e:
            print("Parsing failed:", e)
            parsed_data = {}
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

    if doc_type == "12th_marksheet" and parsed_data.get("percentage"):
        await profiles_col.update_one(
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

    return {
        "ok": True,
        "doc_id": doc_id,
        "parsed_data": parsed_data,
        "extracted_preview": extracted_text[:300],
    }
