import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.db.mongo import get_db
from app.schemas import ChatOut, MessageIn
from app.services import rag
from app.services.auth import current_user
from app.services.conversation import DEFAULT_TITLE, get_owned, make_title, msg_out, oid, utcnow

router = APIRouter(prefix="/api/conversations", tags=["chat"])
log = logging.getLogger("chat")


@router.post("/{conversation_id}/messages", response_model=ChatOut)
async def send_message(conversation_id: str, body: MessageIn, user=Depends(current_user), db=Depends(get_db)):
    conv = await get_owned(db, conversation_id, user["_id"])
    uid, cid = user["_id"], conv["_id"]

    if body.retry_message_id:  # retry: reuse the already-saved user message
        um = await db.messages.find_one({"_id": oid(body.retry_message_id), "conversation_id": cid,
                                         "user_id": uid, "role": "user"})
        if not um:
            raise HTTPException(404, "Message not found")
    else:
        now = utcnow()
        um = {"conversation_id": cid, "user_id": uid, "role": "user", "content": body.content, "created_at": now}
        um["_id"] = (await db.messages.insert_one(um)).inserted_id
        upd = {"last_message_at": now, "updated_at": now}
        if conv["title"] == DEFAULT_TITLE:
            upd["title"] = make_title(body.content)
        await db.conversations.update_one({"_id": cid}, {"$set": upd})

    cur = db.messages.find({"conversation_id": cid, "user_id": uid, "_id": {"$ne": um["_id"]}}).sort([("created_at", -1), ("_id", -1)]).limit(10)
    history = [{"role": m["role"], "content": m["content"]} async for m in cur][::-1]

    try:
        text, sources = await rag.answer(um["content"], history)
    except Exception:  # never save a fake assistant answer
        log.exception("Generation failed")
        return JSONResponse(status_code=502, content={
            "message": "The assistant is unavailable right now. Your message was saved - please retry.",
            "user_message": msg_out(um)})

    now = utcnow()
    am = {"conversation_id": cid, "user_id": uid, "role": "assistant", "content": text,
          "created_at": now, "sources": sources}
    am["_id"] = (await db.messages.insert_one(am)).inserted_id
    await db.conversations.update_one({"_id": cid}, {"$set": {"last_message_at": now, "updated_at": now}})
    return {"user_message": msg_out(um), "assistant_message": msg_out(am)}

