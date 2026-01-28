from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.deps import auth
from app.db.mongo import profiles_col, chats_col
from fastapi import Request

router = APIRouter()


class AskRequest(BaseModel):
    question: str


@router.post("/api/ask")
async def ask(payload: AskRequest, request: Request, user=Depends(auth)):
    profile = await profiles_col.find_one({"user_id": user.get("user_id")})
    if not profile:
        raise HTTPException(status_code=400, detail="Profile not found")

    combined_input = f"""
User Profile:
State: {profile.get('state')}
Category: {profile.get('category')}
Income: {profile.get('income')}
Marks: {profile.get('education', {}).get('class_12_marks')}

Question:
{payload.question}
"""
    qa_chain = request.app.state.qa_chain
    result = qa_chain.invoke({"input": combined_input})

    answer = result.get("answer", "No response")
    docs = result.get("context", [])

    # Save chat
    await chats_col.insert_one({
        "user_id": user.get("user_id"),
        "question": payload.question,
        "answer": answer,
        "sources": [d.metadata.get("source") for d in docs]
    })

    return {"response": answer, "sources": list({d.metadata.get("source") for d in docs})}
