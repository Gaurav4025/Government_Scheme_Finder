import os
import uuid
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from PIL import Image
import easyocr
from pathlib import Path
from dotenv import load_dotenv
from markupsafe import Markup

from fastapi import FastAPI, Request, Form, HTTPException, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from dotenv import load_dotenv
from markupsafe import Markup

from app.repo import (
    list_conversations,
    create_conversation,
    get_conversation,
    get_messages,
    add_message,
    rename_conversation,
    delete_conversation,
    get_profile,
)

from app.components.retriever import create_qa_chain
from app.components.vector_store import load_vector_store
from app.auth.routes import router as auth_router
from app.profile.routes import router as profile_router
from app.documents.routes import router as documents_router
from app.ai.routes import router as ai_router
from app.auth.deps import auth

load_dotenv()

app = FastAPI(
    title="Smart Govt Scheme Finder",
    description="AI-powered eligibility checker for Indian government schemes",
    version="1.0.0",
)


FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

def nl2br(value: str):
    return Markup(value.replace("\n", "<br>\n"))

templates.env.filters["nl2br"] = nl2br


def build_user_context(profile: dict) -> str:
    """
    Build user context from profile data.
    The profile already contains parsed marksheet data from OCR.
    """
    context = f"""
USER PROFILE (VERIFIED FROM DATABASE):
- Name: {profile.get("name", "Not provided")}
- Date of Birth: {profile.get("dob", "Not provided")}
- State: {profile.get("state", "Not provided")}
- Category: {profile.get("category", "Not provided")}
- Annual Income: {profile.get("income", "Not provided")}

EDUCATION DETAILS (OCR VERIFIED):
- Class 12 Board: {profile.get("board_12", "Not available")}
- Class 12 Marks: {profile.get("marks_12", "Not available")}{'%' if profile.get("marks_12") else ''}
- Year: {profile.get("year_12", "Not available")}
- Result: {profile.get("result_12", "Not available")}
"""
    print(f"\n{'='*60}")
    print("DEBUG - USER CONTEXT BEING SENT TO LLM:")
    print(f"{'='*60}")
    print(context)
    print(f"{'='*60}\n")
    
    return context


@app.on_event("startup")
async def startup_event():
    print("Starting application...")
    try:
        print("Loading vector store...")
        vector_store = load_vector_store()
        if vector_store is None:
            print("⚠️  Vector store is None (may not exist or failed to load)")
            app.state.qa_chain = None
        else:
    
            from app.components.vector_store import load_vector_store
            from app.components.retriever import create_qa_chain

            app.state.qa_chain = create_qa_chain()


        print("Application startup complete")

    except Exception as e:
        app.state.qa_chain = None
        print(f"❌ Failed to create QA chain on startup: {e}")
        import traceback
        traceback.print_exc()

    print("Application startup complete")


@app.post("/c/{conversation_id}")
async def send_message(
    request: Request,
    conversation_id: str,  # Changed from int to str for MongoDB ObjectId
    prompt: str = Form(...),
    user=Depends(auth),
):
    user_input = prompt.strip()
    if not user_input:
        return RedirectResponse(url=f"/c/{conversation_id}", status_code=303)

    await add_message(conversation_id, "user", user_input)

    try:
        # Get user profile from MongoDB (contains all data including parsed marksheet info)
        profile = await get_profile(user["user_id"])
        
        print(f"\n{'='*60}")
        print(f"DEBUG - Profile fetched from MongoDB for user: {user['user_id']}")
        print(f"{'='*60}")
        print(f"Profile data: {profile}")
        print(f"{'='*60}\n")
        
        if not profile:
            await add_message(
                conversation_id,
                "assistant",
                "Please complete your profile before asking eligibility questions.",
                sources=[],
            )
            return RedirectResponse(url=f"/c/{conversation_id}", status_code=303)

        # Build context from profile
        user_context = build_user_context(profile)

        combined_input = f"""
{user_context}

USER QUESTION:
{user_input}
"""

        qa_chain = request.app.state.qa_chain
        response = qa_chain.invoke({"input": combined_input})

        answer = response.get("answer", "No response")
        docs = response.get("context", [])

        sources_list = []
        for d in docs[:3]:
            sources_list.append({
                "source": os.path.basename(d.metadata.get("source", "Unknown")),
                "page": d.metadata.get("page", "NA"),
                "snippet": d.page_content[:240],
            })

        await add_message(conversation_id, "assistant", answer, sources=sources_list)

        convo = await get_conversation(conversation_id)
        if convo and convo["title"] == "New Chat":
            await rename_conversation(conversation_id, user_input[:40].strip())

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"ERROR in send_message: {str(e)}")
        print(f"{'='*60}\n")
        import traceback
        traceback.print_exc()
        await add_message(
            conversation_id,
            "assistant",
            f"Internal error: {str(e)}",
            sources=[],
        )

    return RedirectResponse(url=f"/c/{conversation_id}", status_code=303)


# DEBUG ENDPOINT
@app.get("/debug/check-profile/{user_id}")
async def debug_check_profile(user_id: str):
    """Debug endpoint to check what's in MongoDB profile"""
    from app.db.mongo import profiles_col
    
    profile = await profiles_col.find_one({"user_id": user_id})
    
    if profile:
        profile["_id"] = str(profile["_id"])
    
    return {
        "found": profile is not None,
        "profile": profile,
        "has_marksheet_data": bool(profile and profile.get("marks_12"))
    }


app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(documents_router)
app.include_router(ai_router)