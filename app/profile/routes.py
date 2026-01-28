from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.db.mongo import profiles_col
from app.auth.deps import auth

router = APIRouter()

class BasicProfile(BaseModel):
    name: str
    dob: str
    state: str


@router.post("/api/profile/basic")
async def save_basic(data: BasicProfile, user=Depends(auth)):
    await profiles_col.update_one(
        {"user_id": user["user_id"]},
        {"$set": data.dict()},
        upsert=True
    )
    return {"ok": True}
