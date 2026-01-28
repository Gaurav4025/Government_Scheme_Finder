import os
import uuid
import jwt
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
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
from app.components.vector_store import load_vector_store
from app.components.retriever import create_qa_chain


from app.db import init_db
from app.repo import (
    list_conversations, create_conversation, get_conversation,
    get_messages, add_message, rename_conversation, delete_conversation,
    create_user, get_user_by_email, get_user_by_id,
    save_profile, get_profile, save_document, get_user_documents, get_document_text
)
from app.components.retriever import create_qa_chain


load_dotenv()

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

# Configure CORS: allow the frontend origin (defaults to Vite dev server)
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


@app.on_event("startup")
async def startup_event():
    try:
        print("Starting application...")

        init_db()

        vector_store = load_vector_store()
        if vector_store is None:
            raise RuntimeError("Vector store failed to load; check your vectorstore files")
        app.state.vector_store = vector_store

        app.state.qa_chain = create_qa_chain(vector_store)

        print("Application startup complete")

    except Exception as e:
        print("Startup failed:", e)
        raise RuntimeError("QA system failed to initialize")



@app.get("/", response_class=HTMLResponse)
async def home():
    convos = list_conversations()
    if convos:
        return RedirectResponse(url=f"/c/{convos[0]['id']}", status_code=303)

    cid = create_conversation("New Chat")
    return RedirectResponse(url=f"/c/{cid}", status_code=303)


@app.post("/new")
async def new_chat():
    cid = create_conversation("New Chat")
    return RedirectResponse(url=f"/c/{cid}", status_code=303)


@app.get("/c/{conversation_id}", response_class=HTMLResponse)
async def chat_page(request: Request, conversation_id: int):
    convo = get_conversation(conversation_id)
    if convo is None:
        return RedirectResponse(url="/", status_code=303)

    convos = list_conversations()
    msgs = get_messages(conversation_id)

    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "conversations": convos,
            "active_id": conversation_id,
            "messages": msgs,
            "title": convo["title"],
        },
    )


@app.post("/c/{conversation_id}")
async def send_message(request: Request, conversation_id: int, prompt: str = Form(...)):
    user_input = prompt.strip()
    if not user_input:
        return RedirectResponse(url=f"/c/{conversation_id}", status_code=303)

    add_message(conversation_id, "user", user_input)

    try:
        qa_chain = request.app.state.qa_chain

        response = qa_chain.invoke({"input": user_input})

        result = response.get("answer", "No response")

        docs = response.get("context", [])

        sources_list = []
        for d in docs[:3]:
            sources_list.append({
                "source": os.path.basename(d.metadata.get("source", "Unknown")),
                "page": d.metadata.get("page", "NA"),
                "snippet": d.page_content[:240],
            })

        add_message(conversation_id, "assistant", result, sources=sources_list)

        convo = get_conversation(conversation_id)
        if convo and convo["title"] == "New Chat":
            title = user_input[:40].strip()
            rename_conversation(conversation_id, title)

    except Exception as e:
        add_message(conversation_id, "assistant", f"Error: {str(e)}", sources=[])

    return RedirectResponse(url=f"/c/{conversation_id}", status_code=303)


@app.post("/c/{conversation_id}/delete")
async def delete_chat(conversation_id: int):
    delete_conversation(conversation_id)
    return RedirectResponse(url="/", status_code=303)


from pydantic import BaseModel
from typing import Optional, Dict, Any
class EligibilityRequest(BaseModel):
    user_data: Dict[str, Any]
    question: str


@app.post("/api/test-eligibility")
async def test_eligibility(request: Request, payload: EligibilityRequest):
    qa_chain = request.app.state.qa_chain

    user_data = payload.user_data
    question = payload.question

    combined_input = f"""
User Data:
- Class 12 Marks: {user_data.get("marks_12")}
- Annual Income: {user_data.get("income")}
- State: {user_data.get("state")}
- Category: {user_data.get("category")}

User Question:
{question}
"""

    result = qa_chain.invoke({
        "input": combined_input
    })

    docs = result.get("context", [])
    answer = result.get("answer", "")

    sources = list(
        set(doc.metadata.get("source", "Unknown") for doc in docs)
    )

    return {
        "response": answer,
        "sources": sources
    }


# Pydantic models for API
class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ProfileRequest(BaseModel):
    name: str
    dob: str
    state: str
    income: int
    category: str

class AskRequest(BaseModel):
    question: str


# Auth endpoints
@app.post("/api/register")
async def register(payload: RegisterRequest):
    user = get_user_by_email(payload.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(payload.password)
    if not create_user(user_id, payload.email, hashed_password):
        raise HTTPException(status_code=400, detail="Registration failed")

    access_token = create_access_token(data={"sub": user_id})
    return {"token": access_token, "user_id": user_id}


@app.post("/api/login")
async def login(payload: LoginRequest):
    user = get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user["id"]})
    return {"token": access_token, "user_id": user["id"]}


# Profile endpoints
@app.post("/api/profile/basic")
async def save_basic_profile(payload: ProfileRequest, user_id: str = Depends(verify_token)):
    save_profile(user_id, payload.name, payload.dob, payload.state, payload.income, payload.category)
    return {"ok": True}


@app.get("/api/profile")
async def get_user_profile(user_id: str = Depends(verify_token)):
    profile = get_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    documents = get_user_documents(user_id)
    return {
        "name": profile["name"],
        "state": profile["state"],
        "category": profile["category"],
        "documents": [{"doc_id": doc["id"], "doc_type": doc["doc_type"]} for doc in documents]
    }


# Document upload endpoint
@app.post("/api/upload-document")
async def upload_document(doc_type: str = Form(...), file: UploadFile = File(...), user_id: str = Depends(verify_token)):
    # Save file
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{user_id}_{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # OCR processing
    reader = easyocr.Reader(['en'])
    result = reader.readtext(str(file_path))
    extracted_text = " ".join([text for (_, text, _) in result])

    # Save to DB
    doc_id = str(uuid.uuid4())
    save_document(doc_id, user_id, doc_type, str(file_path), extracted_text)

    return {"ok": True, "doc_id": doc_id, "extracted_preview": extracted_text[:100] + "..."}


# Ask AI endpoint
@app.post("/api/ask")
async def ask_ai(payload: AskRequest, user_id: str = Depends(verify_token)):
    qa_chain = app.state.qa_chain

    # Get user profile and documents
    profile = get_profile(user_id)
    doc_text = get_document_text(user_id)

    combined_input = f"""
User Profile:
- Name: {profile['name'] if profile else 'Unknown'}
- DOB: {profile['dob'] if profile else 'Unknown'}
- State: {profile['state'] if profile else 'Unknown'}
- Income: {profile['income'] if profile else 'Unknown'}
- Category: {profile['category'] if profile else 'Unknown'}

User Documents:
{doc_text}

User Question:
{payload.question}
"""

    result = qa_chain.invoke({"input": combined_input})
    docs = result.get("context", [])
    answer = result.get("answer", "")

    sources = list(set(doc.metadata.get("source", "Unknown") for doc in docs))

    return {"response": answer, "sources": sources}

