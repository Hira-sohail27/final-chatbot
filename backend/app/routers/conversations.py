from fastapi import APIRouter, Depends, Query, Response
from app.db.mongo import get_db
from app.schemas import ConvDetail, ConvOut, RenameIn
from app.services.auth import current_user
from app.services.conversation import DEFAULT_TITLE, conv_out, get_owned, msg_out, utcnow

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.post("", response_model=ConvOut, status_code=201)
async def create(user=Depends(current_user), db=Depends(get_db)):
    now = utcnow()
    doc = {"user_id": user["_id"], "title": DEFAULT_TITLE, "created_at": now, "updated_at": now,
           "last_message_at": now}
    doc["_id"] = (await db.conversations.insert_one(doc)).inserted_id
    return conv_out(doc)


@router.get("", response_model=list[ConvOut])
async def list_all(limit: int = Query(100, ge=1, le=200), user=Depends(current_user), db=Depends(get_db)):
    cur = db.conversations.find({"user_id": user["_id"]}).sort("last_message_at", -1).limit(limit)
    return [conv_out(d) async for d in cur]


@router.get("/{conversation_id}", response_model=ConvDetail)
async def get_one(conversation_id: str, limit: int = Query(100, ge=1, le=200),
                  user=Depends(current_user), db=Depends(get_db)):
    conv = await get_owned(db, conversation_id, user["_id"])
    cur = db.messages.find({"conversation_id": conv["_id"], "user_id": user["_id"]}).sort([("created_at", -1), ("_id", -1)]).limit(limit)
    msgs = [msg_out(m) async for m in cur]
    return {"conversation": conv_out(conv), "messages": msgs[::-1]}


@router.patch("/{conversation_id}", response_model=ConvOut)
async def rename(conversation_id: str, body: RenameIn, user=Depends(current_user), db=Depends(get_db)):
    conv = await get_owned(db, conversation_id, user["_id"])
    conv["title"], conv["updated_at"] = body.title, utcnow()
    await db.conversations.update_one({"_id": conv["_id"]}, {"$set": {"title": conv["title"], "updated_at": conv["updated_at"]}})
    return conv_out(conv)


@router.delete("/{conversation_id}", status_code=204)
async def delete(conversation_id: str, user=Depends(current_user), db=Depends(get_db)):
    conv = await get_owned(db, conversation_id, user["_id"])
    await db.messages.delete_many({"conversation_id": conv["_id"]})
    await db.conversations.delete_one({"_id": conv["_id"]})
    return Response(status_code=204)

