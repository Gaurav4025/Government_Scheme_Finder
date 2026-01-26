from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
import os
from app.auth.deps import auth
from app.db.mongo import documents_col, profiles_col
from app.documents.ocr import extract_text

router = APIRouter()


@router.post("/api/upload-document")
async def upload_doc(file: UploadFile = File(...), doc_type: str = Form(...), user=Depends(auth)):
    user_id = user.get("user_id")
    user_dir = os.path.join("storage", user_id)
    os.makedirs(user_dir, exist_ok=True)
    path = os.path.join(user_dir, file.filename)
    content = await file.read()
    with open(path, "wb") as f:
        f.write(content)

    # Run OCR and store metadata
    try:
        extracted = extract_text(path)
    except Exception:
        extracted = ""

    doc = {
        "user_id": user_id,
        "doc_type": doc_type,
        "filename": file.filename,
        "path": path,
        "extracted_text": extracted,
    }
    res = await documents_col.insert_one(doc)

    # Optionally update profile with document summary
    await profiles_col.update_one({"user_id": user_id}, {"$push": {"documents": doc}}, upsert=True)

    return {"ok": True, "doc_id": str(res.inserted_id)}
