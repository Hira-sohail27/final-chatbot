# Full-Stack AI Chatbot (React + Tailwind, FastAPI + Pydantic, MongoDB + Qdrant)

## Architecture
- **frontend/**: React (Vite) + Tailwind. Components: `AuthPage`, `Sidebar` (date-grouped history, rename, delete), `ChatWindow`, `Message`, `Composer`.
- **backend/**: FastAPI. `routers/` (auth, conversations, chat) → `services/` (auth, conversation, llm, rag) → `db/` (Mongo, Qdrant). `schemas/` holds Pydantic models, `core/config.py` loads env vars.
- **MongoDB** = source of truth (users, conversations, messages). **Qdrant** = vectors for knowledge-base retrieval only.
- Auth: bcrypt password hashes + JWT bearer token (24h expiry, stored in `localStorage`). Logout is stateless: the client discards the token.
- Chat flow: save user message → retrieve chunks from Qdrant → LLM answer → save assistant message. If the LLM/Qdrant fails, the user message stays saved, **no fake answer is stored**, and the UI shows Retry.
- History groups (Today / Yesterday / Previous 7 Days / Older) are computed in the browser from `last_message_at` using the user's local timezone (server stores UTC).
- Indexes: unique `users.email`; `conversations(user_id, last_message_at)`; `messages(conversation_id, created_at)`.

## Setup
Requires Python 3.11+, Node 18+, MongoDB (local or Atlas), and a free Gemini API key. Qdrant runs in embedded local mode by default (no server). To use a Qdrant server/cloud instead, set `QDRANT_URL` and `QDRANT_API_KEY`.
```bash
# Start MongoDB (local install or Atlas) and put its URI in .env

cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # fill LLM_API_KEY, JWT_SECRET and MONGO_URI
python -m scripts.index_kb  # creates Qdrant collection + indexes kb/company_faq.txt
uvicorn app.main:app --port 8000   # (do not use --reload with embedded Qdrant)

cd ../frontend
npm install && npm run dev  # http://localhost:5173
```
Tests: `cd backend && pytest` (uses an in-memory Mongo mock; the LLM is stubbed).

## Environment variables
See `.env.example` (MONGO_URI, MONGO_DB, QDRANT_URL, QDRANT_API_KEY, QDRANT_PATH, QDRANT_COLLECTION, LLM_API_KEY, LLM_BASE_URL, CHAT_MODEL, EMBED_MODEL, EMBED_DIM, RAG_MIN_SCORE, JWT_SECRET, JWT_EXPIRE_MINUTES, CORS_ORIGIN).

## API
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/register | Create account (409 on duplicate email) |
| POST | /api/auth/login | Returns JWT + user |
| POST | /api/auth/logout | Client discards token |
| GET | /api/auth/me | Current user |
| POST | /api/conversations | New conversation |
| GET | /api/conversations | Own conversations, newest first |
| GET | /api/conversations/{id}?limit=100 | Conversation + last N messages |
| PATCH | /api/conversations/{id} | Rename |
| DELETE | /api/conversations/{id} | Delete (and its messages) |
| POST | /api/conversations/{id}/messages | Send message (`retry_message_id` optional) |

Other users' IDs always return 404. Interactive docs: http://localhost:8000/docs
