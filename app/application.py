import os
from dotenv import load_dotenv
from markupsafe import Markup

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles



from app.sqlite_db import init_db
from app.repo import (
    list_conversations, create_conversation, get_conversation,
    get_messages, add_message, rename_conversation, delete_conversation
)
from app.components.retriever import create_qa_chain


load_dotenv()

app = FastAPI(
    title="Smart Govt Scheme Finder",
    description="AI-powered eligibility checker for Indian government schemes",
    version="1.0.0"
)


from fastapi.middleware.cors import CORSMiddleware


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

        if os.getenv("MOCK_QA", "false").lower() in ("1", "true", "yes"):
            class MockChain:
                def invoke(self, payload):
                    return {"answer": "This is a mock response (set MOCK_QA=false to use real models).", "context": []}

            app.state.qa_chain = MockChain()
        else:
    
            from app.components.vector_store import load_vector_store
            from app.components.retriever import create_qa_chain

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


from app.auth.routes import router as auth_router
from app.profile.routes import router as profile_router
from app.documents.routes import router as documents_router
from app.ai.routes import router as ai_router

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(documents_router)
app.include_router(ai_router)

