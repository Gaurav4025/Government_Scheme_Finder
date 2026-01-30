import json
from app.db.mongo import profiles_col, chats_col, users_col, documents_col, db
from typing import Optional
import bcrypt
from datetime import datetime


# ==================== CONVERSATIONS ====================

async def list_conversations(user_id: str):
    """List all conversations for a user"""
    conversations = await chats_col.find(
        {"user_id": user_id}
    ).sort("created_at", -1).to_list(length=None)
    
    return [
        {
            "id": str(chat["_id"]),
            "title": chat.get("title", "New Chat"),
            "created_at": chat.get("created_at", "")
        }
        for chat in conversations
    ]


async def create_conversation(user_id: str, title="New Chat"):
    """Create a new conversation"""
    conversation = {
        "user_id": user_id,
        "title": title,
        "created_at": datetime.utcnow().isoformat(),
        "messages": []
    }
    result = await chats_col.insert_one(conversation)
    return str(result.inserted_id)


async def get_conversation(conversation_id: str):
    """Get a single conversation by ID"""
    from bson import ObjectId
    
    try:
        chat = await chats_col.find_one({"_id": ObjectId(conversation_id)})
        if chat:
            return {
                "id": str(chat["_id"]),
                "title": chat.get("title", "New Chat")
            }
    except:
        pass
    return None


async def get_messages(conversation_id: str):
    """Get all messages in a conversation"""
    from bson import ObjectId
    
    try:
        chat = await chats_col.find_one({"_id": ObjectId(conversation_id)})
        if chat:
            messages = chat.get("messages", [])
            return [
                {
                    "role": msg.get("role"),
                    "content": msg.get("content"),
                    "sources": msg.get("sources", []),
                    "created_at": msg.get("created_at", "")
                }
                for msg in messages
            ]
    except:
        pass
    return []


async def add_message(conversation_id: str, role: str, content: str, sources=None):
    """Add a message to a conversation"""
    from bson import ObjectId
    
    message = {
        "role": role,
        "content": content,
        "sources": sources or [],
        "created_at": datetime.utcnow().isoformat()
    }
    
    try:
        await chats_col.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$push": {"messages": message}}
        )
    except Exception as e:
        print(f"Error adding message: {e}")


async def rename_conversation(conversation_id: str, title: str):
    """Rename a conversation"""
    from bson import ObjectId
    
    try:
        await chats_col.update_one(
            {"_id": ObjectId(conversation_id)},
            {"$set": {"title": title}}
        )
    except Exception as e:
        print(f"Error renaming conversation: {e}")


async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    from bson import ObjectId
    
    try:
        await chats_col.delete_one({"_id": ObjectId(conversation_id)})
    except Exception as e:
        print(f"Error deleting conversation: {e}")


# ==================== USERS ====================

async def create_user(user_id: str, email: str, password_hash: str):
    """Create a new user"""
    try:
        user = {
            "user_id": user_id,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.utcnow().isoformat()
        }
        await users_col.insert_one(user)
        return user_id
    except Exception as e:
        print(f"Error creating user: {e}")
        return None


async def get_user_by_email(email: str):
    """Get user by email"""
    user = await users_col.find_one({"email": email})
    if user:
        return {
            "id": user.get("user_id"),
            "email": user.get("email"),
            "password_hash": user.get("password_hash")
        }
    return None


async def get_user_by_id(user_id: str):
    """Get user by ID"""
    user = await users_col.find_one({"user_id": user_id})
    if user:
        return {
            "id": user.get("user_id"),
            "email": user.get("email")
        }
    return None


# ==================== PROFILES ====================

async def get_profile(user_id: str):
    """
    Get user profile from MongoDB profiles collection.
    This includes both manually entered data and OCR-parsed data.
    """
    profile = await profiles_col.find_one({"user_id": user_id})
    if profile:
        profile.pop("_id", None)
    return profile


async def save_profile(user_id: str, name: str, dob: str, state: str, income: float, category: str):
    """Save or update user profile in MongoDB"""
    await profiles_col.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "name": name,
                "dob": dob,
                "state": state,
                "income": income,
                "category": category,
                "updated_at": datetime.utcnow().isoformat()
            }
        },
        upsert=True
    )


# ==================== DOCUMENTS ====================

async def save_document(doc_id: str, user_id: str, doc_type: str, file_path: str, extracted_text: str):
    """Save document to MongoDB"""
    doc = {
        "doc_id": doc_id,
        "user_id": user_id,
        "doc_type": doc_type,
        "file_path": file_path,
        "extracted_text": extracted_text,
        "created_at": datetime.utcnow().isoformat()
    }
    await documents_col.insert_one(doc)


async def get_user_documents(user_id: str):
    """Get all documents for a user"""
    docs = await documents_col.find({"user_id": user_id}).to_list(length=None)
    return [
        {
            "id": doc.get("doc_id"),
            "doc_type": doc.get("doc_type"),
            "extracted_text": doc.get("extracted_text", "")
        }
        for doc in docs
    ]


async def get_document_text(user_id: str):
    """Get all extracted text from user documents"""
    docs = await documents_col.find({"user_id": user_id}).to_list(length=None)
    return " ".join([doc.get("extracted_text", "") for doc in docs if doc.get("extracted_text")])