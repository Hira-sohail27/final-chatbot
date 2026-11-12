from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from bson import ObjectId
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
from app.db.mongo import get_db

bearer = HTTPBearer(auto_error=False)


def hash_pw(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()


def verify_pw(p: str, h: str) -> bool:
    return bcrypt.checkpw(p.encode(), h.encode())


def make_token(uid: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    return jwt.encode({"sub": uid, "exp": exp}, settings.jwt_secret, "HS256")


async def current_user(cred: HTTPAuthorizationCredentials | None = Depends(bearer), db=Depends(get_db)):
    if not cred:
        raise HTTPException(401, "Not authenticated")
    try:
        uid = jwt.decode(cred.credentials, settings.jwt_secret, ["HS256"])["sub"]
        user = await db.users.find_one({"_id": ObjectId(uid)})
    except Exception:
        raise HTTPException(401, "Invalid or expired token")
    if not user:
        raise HTTPException(401, "Invalid or expired token")
    return user
