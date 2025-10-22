import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from config.db import get_db, init_db
from models.chat import Session, Interest
from agent.handlers import get_agent_response, get_infer_interests, prompt_generator
from memory.sqlite import ClearMemory, GetHistory


# ============================================================
# Application lifespan management — runs once on startup/shutdown
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database before serving any requests
    init_db()
    print("Database initialized on startup")
    yield  # Control returns to FastAPI for serving requests


# Initialize FastAPI app with lifespan hook
app = FastAPI(lifespan=lifespan)

# Enable CORS for local frontend (Vite/React apps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Middleware: Add a hidden header to every outgoing response
# ============================================================
@app.middleware("http")
async def add_custom_header(request, call_next):
    response = await call_next(request)
    response.headers["X-Brief-Only"] = "true"
    return response


# ============================================================
# Request payload schemas using Pydantic
# ============================================================
class StartSession(BaseModel):
    prompt: str
    consent: bool


class SendMessage(BaseModel):
    sessionId: int
    message: str


# ============================================================
# Start a new chat session
# ============================================================
@app.post("/start-session")
async def start_session(data: StartSession, db: DBSession = Depends(get_db)):
    # Create a dynamic prompt based on the user query
    prompt = await prompt_generator(data.prompt)

    # Create and persist a new chat session
    session = Session(prompt=prompt, consent=data.consent, paused=False)
    db.add(session)
    db.commit()
    db.refresh(session)

    # Generate the first AI message using the given prompt
    initial_message = await get_agent_response(session.id, data.prompt, data.prompt)

    return {"sessionId": session.id, "initialMessage": initial_message}


# ============================================================
# Send a message to the agent and receive its response
# ============================================================
@app.post("/send-message")
async def send_message(data: SendMessage, db: DBSession = Depends(get_db)):
    # Retrieve session and ensure it's active
    session = db.query(Session).filter(Session.id == data.sessionId).first()
    if not session or session.paused:
        raise HTTPException(404, "Session not found or paused")

    # Get the AI response (automatically updates memory history)
    agent_message = await get_agent_response(
        data.sessionId, session.prompt, data.message
    )

    # Infer user interests based on conversation history
    interests = await get_infer_interests(data.sessionId)

    # Replace old interests with new ones in the DB
    db.query(Interest).filter(Interest.session_id == data.sessionId).delete()
    for int in interests:
        db.add(Interest(session_id=data.sessionId, **int))
    db.commit()

    return {"agentMessage": agent_message}


# ============================================================
# Retrieve inferred interests for a specific session
# ============================================================
@app.get("/interests/{sessionId}")
async def get_interests(sessionId: int, db: DBSession = Depends(get_db)):
    interests = (
        db.query(Interest)
        .filter(Interest.session_id == sessionId)
        .order_by(Interest.confidence.desc())
        .all()
    )

    # Return simplified structured list
    return [
        {"name": i.name, "confidence": i.confidence, "rationale": i.rationale}
        for i in interests
    ]


# ============================================================
# Pause a session (temporarily disable chat)
# ============================================================
@app.post("/pause/{sessionId}")
async def pause_session(sessionId: int, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == sessionId).first()
    if session:
        session.paused = True
        db.commit()
    return {"status": "paused"}


# ============================================================
# Resume a previously paused session
# ============================================================
@app.post("/resume/{sessionId}")
async def resume_session(sessionId: int, db: DBSession = Depends(get_db)):
    session = db.query(Session).filter(Session.id == sessionId).first()
    if session:
        session.paused = False
        db.commit()
    return {"status": "resumed"}


# ============================================================
# Retrieve session info (used to check session state)
# ============================================================
@app.get("/session/{sessionId}")
async def get_session(sessionId: int, db: DBSession = Depends(get_db)):
    """
    Fetch a session by ID — verifies its existence and status.
    """
    session = db.query(Session).filter(Session.id == sessionId).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "id": session.id,
        "paused": session.paused,
        "consent": session.consent,
    }


# ============================================================
# Delete a session and all related data
# ============================================================
@app.delete("/session/{sessionId}")
async def delete_session(sessionId: int, db: DBSession = Depends(get_db)):
    # Fetch the session first
    session = db.query(Session).filter(
        Session.id == sessionId, Session.deleted == False).first()
    if not session:
        raise HTTPException(
            status_code=404, detail="Session not found or already deleted")

    # Mark related interests as deleted
    db.query(Interest).filter(Interest.session_id ==
                              sessionId).update({"deleted": True})

    # Mark the session as deleted
    session.deleted = True

    # Clear in-memory chat history (SQLite memory backend)
    ClearMemory(session_id=sessionId)

    db.commit()
    return {"status": "deleted"}


# ============================================================
# List all existing sessions
# ============================================================
@app.get("/sessions")
async def get_sessions(db: DBSession = Depends(get_db)):
    sessions = db.query(Session).filter(Session.deleted == False).all()
    return sessions


# ============================================================
# Get the last N messages for a session (for chat display)
# ============================================================
@app.get("/sessions/{sessionId}/messages")
def get_last_messages(sessionId: int, limit: int = 100):
    """
    Returns the last `limit` non-empty messages from the chat history.
    Useful for frontend chat replay.
    """
    history = GetHistory(session_id=sessionId)
    all_messages = history.messages[-limit:]

    # Filter out blank messages and format for UI
    formatted = [
        {
            "role": "user" if m.type == "human" else "agent",
            "content": m.content,
        }
        for m in all_messages
        if m.content.strip()
    ]

    return {"session_id": sessionId, "messages": formatted}


# ============================================================
# Run FastAPI app using Uvicorn
# ============================================================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
