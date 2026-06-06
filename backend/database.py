"""
database.py - SQLite ORM using SQLAlchemy
Stores call sessions, risk scores, transcripts, and actions taken.
"""

import os
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, Boolean, Text, event
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import StaticPool

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.getenv("DB_PATH", os.path.join(BASE_DIR, "scam_shield.db"))

engine = create_engine(
    f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Enable WAL mode for better concurrent reads
@event.listens_for(engine, "connect")
def _set_wal(dbapi_conn, _):
    dbapi_conn.execute("PRAGMA journal_mode=WAL")
    dbapi_conn.execute("PRAGMA foreign_keys=ON")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────

class CallSession(Base):
    __tablename__ = "call_sessions"

    id          = Column(Integer, primary_key=True, index=True)
    call_sid    = Column(String(64), unique=True, index=True, nullable=False)
    from_number = Column(String(20))
    to_number   = Column(String(20))
    direction   = Column(String(16), default="inbound")  # inbound | outbound

    started_at  = Column(DateTime, default=datetime.utcnow)
    ended_at    = Column(DateTime, nullable=True)
    duration_s  = Column(Integer, nullable=True)

    # Final risk assessment
    final_score = Column(Float, default=0.0)
    risk_label  = Column(String(16), default="safe")  # safe|suspicious|fraud
    status      = Column(String(16), default="active")  # active|completed|blocked

    # AI Voice Analysis
    aiVoiceScore          = Column(Float, default=0.0)
    humanVoiceProbability = Column(Float, default=0.0)
    aiVoiceProbability    = Column(Float, default=0.0)
    voiceClassification   = Column(String(32), default="Uncertain")
    voiceConfidence       = Column(Float, default=0.0)

    # Transcript
    full_transcript = Column(Text, default="")

    # Action taken
    action_taken   = Column(String(32), nullable=True)  # warning_injected|hung_up|none
    action_at      = Column(DateTime, nullable=True)

    # App settings at time of call
    threshold_used = Column(Float, default=0.71)
    auto_hangup    = Column(Boolean, default=True)


class ScoreEvent(Base):
    """Rolling score snapshots during a call (for graphing in the app)."""
    __tablename__ = "score_events"

    id         = Column(Integer, primary_key=True, index=True)
    call_sid   = Column(String(64), index=True, nullable=False)
    timestamp  = Column(DateTime, default=datetime.utcnow)
    score      = Column(Float, nullable=False)
    label      = Column(String(16), nullable=False)
    transcript_chunk = Column(Text, default="")


class AppSettings(Base):
    """Global app configuration (one row, id=1)."""
    __tablename__ = "app_settings"

    id               = Column(Integer, primary_key=True, default=1)
    risk_threshold   = Column(Float, default=0.71)
    auto_hangup      = Column(Boolean, default=True)
    alert_suspicious = Column(Boolean, default=True)
    unknown_only     = Column(Boolean, default=True)   # Only monitor unknown numbers
    forward_to       = Column(String(20), nullable=True)  # user's real number
    expo_push_token  = Column(String(100), nullable=True)  # Expo push token from app
    updated_at       = Column(DateTime, default=datetime.utcnow)


class SavedContact(Base):
    """Phone contacts synced from the mobile app."""
    __tablename__ = "saved_contacts"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(128), nullable=True)
    # Normalized E.164 number, e.g. +919876543210
    phone       = Column(String(20), unique=True, index=True, nullable=False)
    synced_at   = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all tables and seed default settings. Recreates db on schema mismatch."""
    from sqlalchemy.exc import OperationalError
    
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            if not db.query(AppSettings).first():
                db.add(AppSettings())
                db.commit()
        finally:
            db.close()
    except OperationalError as e:
        print(f"[DB] Schema mismatch detected ({e}). Recreating database...")
        # Close engine connection pool
        engine.dispose()
        # Drop all tables first, then recreate
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            db.add(AppSettings())
            db.commit()
        finally:
            db.close()
        print("[DB] Database successfully recreated with new schema.")


def is_known_number(db: Session, phone: str) -> bool:
    """
    Normalize and check if a phone number is in saved contacts.
    Strips spaces, dashes, +91 country code variations.
    """
    import re
    def normalize(n: str) -> str:
        n = re.sub(r'[^\d]', '', str(n))  # digits only
        if len(n) == 12 and n.startswith('91'):
            n = n[2:]  # strip 91 country code
        if len(n) == 11 and n.startswith('0'):
            n = n[1:]  # strip leading 0
        return n[-10:]  # last 10 digits

    normalized_input = normalize(phone)
    contacts = db.query(SavedContact).all()
    for c in contacts:
        if normalize(c.phone) == normalized_input:
            return True
    return False


def get_db() -> Session:
    """FastAPI dependency: yield a db session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────
# Helper functions (used by main.py)
# ─────────────────────────────────────────────

def create_call(db: Session, call_sid: str, from_num: str, to_num: str,
                settings: AppSettings) -> CallSession:
    call = CallSession(
        call_sid       = call_sid,
        from_number    = from_num,
        to_number      = to_num,
        threshold_used = settings.risk_threshold,
        auto_hangup    = settings.auto_hangup,
    )
    db.add(call)
    db.commit()
    db.refresh(call)
    return call


def update_call_score(db: Session, call_sid: str, score: float, label: str,
                       transcript_chunk: str):
    db.add(ScoreEvent(
        call_sid=call_sid, score=score, label=label,
        transcript_chunk=transcript_chunk
    ))
    # Update the call's final score if this is higher (worst-case tracking)
    call = db.query(CallSession).filter_by(call_sid=call_sid).first()
    if call and score > call.final_score:
        call.final_score = score
        call.risk_label  = label
    db.commit()


def close_call(db: Session, call_sid: str, action: str = "none"):
    call = db.query(CallSession).filter_by(call_sid=call_sid).first()
    if call:
        call.ended_at    = datetime.utcnow()
        call.status      = "blocked" if action in ("warning_injected", "hung_up") else "completed"
        call.action_taken = action
        if action != "none":
            call.action_at = datetime.utcnow()
        db.commit()
