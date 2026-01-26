from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.db.mongo import users_col
from app.auth.utils import hash_password, verify_password, create_token
import uuid

router = APIRouter()


class RegisterRequest(BaseModel):
	email: str
	password: str


class LoginRequest(BaseModel):
	email: str
	password: str


@router.post("/api/register")
async def register(payload: RegisterRequest):
	existing = await users_col.find_one({"email": payload.email})
	if existing:
		raise HTTPException(status_code=400, detail="User already exists")

	user_id = str(uuid.uuid4())
	await users_col.insert_one({
		"user_id": user_id,
		"email": payload.email,
		"password_hash": hash_password(payload.password),
	})
	token = create_token(user_id)
	return {"token": token, "user_id": user_id}


@router.post("/api/login")
async def login(payload: LoginRequest):
	user = await users_col.find_one({"email": payload.email})
	if not user:
		raise HTTPException(status_code=401, detail="Invalid credentials")

	if not verify_password(payload.password, user.get("password_hash", "")):
		raise HTTPException(status_code=401, detail="Invalid credentials")

	token = create_token(user["user_id"])
	return {"token": token, "user_id": user["user_id"]}

