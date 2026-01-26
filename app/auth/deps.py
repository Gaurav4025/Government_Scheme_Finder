from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError
from typing import Optional
from app.db.mongo import users_col
from app.auth.utils import SECRET


async def auth(authorization: Optional[str] = Header(None)):
    """Dependency that returns a user dict when provided a valid Bearer token.
    If no Authorization header is present, raises 401.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    try:
        scheme, token = authorization.split()
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")

    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = await users_col.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
