from fastapi import APIRouter, Depends, HTTPException
from pymongo.errors import DuplicateKeyError
from app.db.mongo import get_db
from app.schemas import LoginIn, RegisterIn, TokenOut, UserOut
from app.services.auth import current_user, hash_pw, make_token, verify_pw
from app.services.conversation import utcnow

router = APIRouter(prefix="/api/auth", tags=["auth"])


def user_out(u) -> dict:
    return {"id": str(u["_id"]), "name": u["name"], "email": u["email"]}


@router.post("/register", response_model=TokenOut, status_code=201)
async def register(body: RegisterIn, db=Depends(get_db)):
    email = body.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(409, "Email already registered")
    now = utcnow()
    doc = {"name": body.name, "email": email, "password_hash": hash_pw(body.password),
           "created_at": now, "updated_at": now}
    try:
        doc["_id"] = (await db.users.insert_one(doc)).inserted_id
    except DuplicateKeyError:
        raise HTTPException(409, "Email already registered")
    return {"access_token": make_token(str(doc["_id"])), "user": user_out(doc)}


@router.post("/login", response_model=TokenOut)
async def login(body: LoginIn, db=Depends(get_db)):
    u = await db.users.find_one({"email": body.email.lower()})
    if not u or not verify_pw(body.password, u["password_hash"]):
        raise HTTPException(401, "Invalid email or password")
    return {"access_token": make_token(str(u["_id"])), "user": user_out(u)}


@router.post("/logout")
async def logout(user=Depends(current_user)):
    # Stateless JWT: the client discards the token (documented in README).
    return {"detail": "Logged out"}


@router.get("/me", response_model=UserOut)
async def me(user=Depends(current_user)):
    return user_out(user)
