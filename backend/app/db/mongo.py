import dns.resolver
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Some networks/adapters break the DNS lookup that mongodb+srv:// needs; use public DNS servers instead.
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ["8.8.8.8", "1.1.1.1"]

_client = AsyncIOMotorClient(settings.mongo_uri)


def get_db():
    return _client[settings.mongo_db]


async def init_indexes():
    db = get_db()
    await db.users.create_index("email", unique=True)
    await db.conversations.create_index([("user_id", 1), ("last_message_at", -1)])
    await db.messages.create_index([("conversation_id", 1), ("created_at", 1)])
