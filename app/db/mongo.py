from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)

db = client["chiththi_lm"]
users_col = db["users"]
profiles_col = db["profiles"]
chats_col = db["chats"]
documents_col = db["documents"]
