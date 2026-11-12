from datetime import datetime, timezone
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException

DEFAULT_TITLE = "New Chat"


def utcnow():
    return datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None)


def iso(dt: datetime) -> str:
    return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def oid(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(404, "Not found")


def make_title(text: str) -> str:
    t = " ".join(text.split())
    return t if len(t) <= 50 else t[:50].rstrip() + "…"


def conv_out(d) -> dict:
    return {"id": str(d["_id"]), "title": d["title"], "created_at": iso(d["created_at"]),
            "updated_at": iso(d["updated_at"]), "last_message_at": iso(d["last_message_at"])}


def msg_out(d) -> dict:
    return {"id": str(d["_id"]), "role": d["role"], "content": d["content"],
            "created_at": iso(d["created_at"]), "sources": d.get("sources", [])}


async def get_owned(db, conv_id: str, user_id):
    """Every conversation access goes through here: scoped to the owner."""
    conv = await db.conversations.find_one({"_id": oid(conv_id), "user_id": user_id})
    if not conv:
        raise HTTPException(404, "Conversation not found")
    return conv
