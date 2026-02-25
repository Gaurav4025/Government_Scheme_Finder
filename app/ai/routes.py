from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.deps import auth
from app.db.mongo import profiles_col, chats_col
from fastapi import Request
from typing import Optional

router = APIRouter()


class AskRequest(BaseModel):
    question: str
    source_id: Optional[str] = None


@router.post("/api/ask")
async def ask(payload: AskRequest, request: Request, user=Depends(auth)):
    profile = await profiles_col.find_one({"user_id": user.get("user_id")})
    if not profile:
        raise HTTPException(status_code=400, detail="Profile not found")

    combined_input = f"""
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

USER QUESTION:

{payload.question}
"""
    print(f"\n{'='*60}")
    print("DEBUG - USER CONTEXT BEING SENT TO LLM (from /api/ask):")
    print(f"{'='*60}")
    print(combined_input)
    print(f"{'='*60}\n")
    
    qa_chain = getattr(request.app.state, "qa_chain", None)
    if qa_chain is None:
        raise HTTPException(status_code=500, detail="QA chain not initialized on server")

    try:
        result = qa_chain.invoke({"input": combined_input})
    except Exception as e:
        print(f" QA invocation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"QA invocation failed: {str(e)}")

    answer = result.get("answer", "No response")
    docs = result.get("context", [])
    
    # Safely extract sources from docs (handle missing metadata)
    sources = []
    if docs:
        for doc in docs:
            try:
                source = doc.metadata.get("source") if hasattr(doc, "metadata") else None
                if source:
                    sources.append(source)
            except Exception as e:
                print(f"⚠️  Error extracting source from doc: {e}")
                continue
    
    sources = list(set(sources))  # deduplicate

    # Save chat
    await chats_col.insert_one({
        "user_id": user.get("user_id"),
        "question": payload.question,
        "answer": answer,
        "sources": sources
    })

    return {"response": answer, "sources": sources}
