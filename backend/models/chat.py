from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey
# Import shared Base class (usually from declarative_base)
from .base import Base

# Represents a user chat session or conversation


class Session(Base):
    __tablename__ = "sessions"

    # Primary key column — unique identifier for each session
    id = Column(Integer, primary_key=True, index=True)

    # The initial user prompt or message that started the session
    prompt = Column(String)

    # Whether the user gave consent (e.g., for data usage or analysis)
    consent = Column(Boolean)

    # Indicates if the session is currently paused
    paused = Column(Boolean)


# Represents interests or topics detected within a session
class Interest(Base):
    __tablename__ = "interests"

    # Primary key for each interest record
    id = Column(Integer, primary_key=True, index=True)

    # Foreign key linking this interest to a specific session
    session_id = Column(Integer, ForeignKey("sessions.id"))

    # The name or label of the detected interest/topic
    name = Column(String)

    # Confidence score (e.g., from an ML model) — how sure we are about this interest
    confidence = Column(Float)

    # The reasoning or explanation for why this interest was assigned
    rationale = Column(String)
