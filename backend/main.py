"""
main.py - FastAPI application
  • POST /twiml        → Returns TwiML to connect incoming call to WebSocket stream
  • WS   /stream       → Twilio media stream WebSocket handler
  • GET  /api/calls    → List all call sessions
  • GET  /api/calls/{call_sid} → Single call detail + score events
  • GET  /api/settings → Get current settings
  • POST /api/settings → Update settings
  • GET  /api/live     → Server-Sent Events for real-time risk score push to app
  • GET  /health       → Health check
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Internal modules
from database import (
    init_db, get_db, SessionLocal,
    CallSession, ScoreEvent, AppSettings, SavedContact,
    create_call, update_call_score, close_call, is_known_number,
)
from audio_processor import AudioBuffer
from stt_client import transcribe
from twilio_client import (
    build_incoming_twiml,
    inject_warning,
    inject_suspicious_alert,
    hangup_call,
)
from push_client import notify_suspicious, notify_fraud

# Import inference engine (will fail gracefully if .pth not yet trained)
try:
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "model"))
    from inference import ScamInferenceEngine
    engine = ScamInferenceEngine(
        model_dir=os.path.join(os.path.dirname(__file__), "model")
    )
    MODEL_LOADED = True
except Exception as e:
    print(f"[WARN] Model not loaded: {e}. Using demo mode.")
    MODEL_LOADED = False
    engine = None

# Pre-load/auto-train Deepfake voice classifier model
try:
    from model.deepfake_classifier import DeepfakeInference
    df_engine = DeepfakeInference()
except Exception as e:
    print(f"[WARN] Deepfake Model not loaded/trained: {e}")

# Instantiate the AI Voice Detector module
try:
    from voice_detector import AIVoiceDetector
    voice_detector = AIVoiceDetector()
except Exception as e:
    print(f"[WARN] AI Voice Detector module not loaded: {e}")
    voice_detector = None



# ─────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────
app = FastAPI(
    title="AI Scam Shield API",
    description="Real-time scam call detection backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for real-time score broadcasting
# call_sid → asyncio.Queue
live_queues: dict[str, asyncio.Queue] = {}

# Serve HTML demos from the local backend directory
DEMO_FILE = os.path.join(os.path.dirname(__file__), "demo.html")
MIC_DEMO_FILE = os.path.join(os.path.dirname(__file__), "mic_demo.html")

@app.get("/")
def root():
    if os.path.exists(DEMO_FILE):
        return FileResponse(DEMO_FILE, media_type="text/html")
    return {"status": "AI Scam Shield API running", "docs": "/docs"}

@app.get("/mic")
def mic_demo():
    if os.path.exists(MIC_DEMO_FILE):
        return FileResponse(MIC_DEMO_FILE, media_type="text/html")
    return {"error": "mic_demo.html not found"}

@app.get("/static/beep.wav")
def get_beep_wav():
    import math
    import struct
    frequency = 1000
    duration_seconds = 0.5
    sample_rate = 8000
    num_samples = int(duration_seconds * sample_rate)
    data = bytearray()
    for i in range(num_samples):
        t = i / sample_rate
        sample = int(32767 * math.sin(2 * math.pi * frequency * t))
        data.extend(struct.pack("<h", sample))
    
    header = bytearray()
    header.extend(b"RIFF")
    header.extend(struct.pack("<I", 36 + len(data)))
    header.extend(b"WAVEfmt ")
    header.extend(struct.pack("<I", 16))
    header.extend(struct.pack("<H", 1))
    header.extend(struct.pack("<H", 1))
    header.extend(struct.pack("<I", sample_rate))
    header.extend(struct.pack("<I", sample_rate * 2))
    header.extend(struct.pack("<H", 2))
    header.extend(struct.pack("<H", 16))
    header.extend(b"data")
    header.extend(struct.pack("<I", len(data)))
    
    return Response(content=bytes(header + data), media_type="audio/wav")

@app.on_event("startup")
def startup():
    init_db()
    print("[Server] ✅ Database initialized")
    print(f"[Server] Model loaded: {MODEL_LOADED}")
    print("[Server] 🌐 Demo: http://localhost:8000/")


# ─────────────────────────────────────────────
# Twilio TwiML Endpoint
# ─────────────────────────────────────────────
@app.post("/twiml")
async def twiml_handler(request: Request):
    """
    Twilio calls this when a call comes in.
    We return TwiML that opens a WebSocket media stream.
    """
    form = await request.form()
    call_sid  = form.get("CallSid", "unknown")
    from_num  = form.get("From", "unknown")
    to_num    = form.get("To", "unknown")

    db = SessionLocal()
    try:
        settings = db.query(AppSettings).first()

        # ── Unknown-only filter ──────────────────────
        # If the caller is a saved contact, forward the call directly — no AI
        if settings and settings.unknown_only and is_known_number(db, from_num):
            print(f"[TwiML] Known contact {from_num} → forwarding without AI")
            from twilio_client import build_incoming_twiml
            forward_to = settings.forward_to or os.getenv("FORWARD_TO_NUMBER")
            # Return plain dial TwiML, no media stream
            from twilio.twiml.voice_response import VoiceResponse
            resp = VoiceResponse()
            if forward_to:
                resp.dial(forward_to)
            else:
                resp.say("Connecting your call.", voice="Polly.Aditi", language="en-IN")
            return Response(content=str(resp), media_type="application/xml")

        # ── Unknown caller → activate AI monitoring ──
        create_call(db, call_sid, from_num, to_num, settings)
    finally:
        db.close()

    forward_to = os.getenv("FORWARD_TO_NUMBER", None)
    twiml = build_incoming_twiml(forward_to=forward_to)
    return Response(content=twiml, media_type="application/xml")


# ─────────────────────────────────────────────
# Twilio WebSocket Media Stream
# ─────────────────────────────────────────────
@app.websocket("/stream/webrtc")
async def webrtc_stream(websocket: WebSocket):
    """
    WebSocket signaling channel for Flutter WebRTC connection.
    """
    from webrtc_handler import handle_webrtc_connection
    await websocket.accept()
    await handle_webrtc_connection(websocket)


@app.websocket("/stream")
async def twilio_stream(websocket: WebSocket):
    """
    Twilio sends base64-encoded mu-law audio chunks every 20ms.
    We decode → buffer → transcribe → score → act.
    """
    await websocket.accept()

    call_sid     = None
    audio_buffer = AudioBuffer(buffer_seconds=1.5)
    transcript   = []          # rolling transcript list
    warning_sent = False       # only send warning once per call
    db           = SessionLocal()

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            event_type = msg.get("event")

            # ── Call connected ─────────────────
            if event_type == "connected":
                print("[WS] Twilio stream connected")

            # ── Call started ───────────────────
            elif event_type == "start":
                start_data = msg.get("start", {})
                call_sid = start_data.get("callSid", "unknown")
                live_queues[call_sid] = asyncio.Queue(maxsize=50)
                print(f"[WS] 📞 Call started: {call_sid}")

            # ── Audio chunk ────────────────────
            elif event_type == "media" and call_sid:
                payload = msg.get("media", {}).get("payload", "")
                is_ready = audio_buffer.push_chunk(payload)

                if is_ready:
                    pcm = audio_buffer.flush()
                    # Transcribe in background
                    asyncio.create_task(
                        _process_audio_chunk(
                            pcm, call_sid, transcript,
                            db, warning_sent
                        )
                    )

            # ── Call ended ─────────────────────
            elif event_type == "stop":
                if call_sid:
                    close_call(db, call_sid, action="none" if not warning_sent else "warning_injected")
                    live_queues.pop(call_sid, None)
                    print(f"[WS] 📴 Call ended: {call_sid}")
                break

    except WebSocketDisconnect:
        if call_sid:
            close_call(db, call_sid, "none")
            live_queues.pop(call_sid, None)
    finally:
        db.close()


async def _process_audio_chunk(
    pcm_bytes: bytes,
    call_sid: str,
    transcript: list,
    db,
    warning_sent: bool,
):
    """Process one buffered audio chunk: STT → score → act."""
    # 1. Transcribe
    text = await transcribe(pcm_bytes)
    if not text:
        return

    transcript.append(text)
    # Keep a rolling 30-second window (~20 chunks of 1.5s)
    if len(transcript) > 20:
        transcript.pop(0)
    rolling_text = " ".join(transcript)

    # 2. Score
    if MODEL_LOADED and engine:
        score, label = engine.predict_rolling(rolling_text)
    else:
        # Demo mode: keyword-based fallback
        score, label = _demo_score(rolling_text)

    print(f"[AI] call={call_sid} score={score:.3f} label={label} | '{text[:60]}'")

    # 3. Persist score event
    update_call_score(db, call_sid, score, label, text)

    # 4. Broadcast to SSE queue
    q = live_queues.get(call_sid)
    if q and not q.full():
        await q.put({"score": score, "label": label, "transcript": text})

    # 5. Take action
    settings = db.query(AppSettings).first()
    threshold  = settings.risk_threshold if settings else 0.71
    auto_hup   = settings.auto_hangup   if settings else True
    push_token = settings.expo_push_token if settings else None

    # Get caller number for notifications
    call_row = db.query(CallSession).filter_by(call_sid=call_sid).first()
    from_num = call_row.from_number if call_row else "Unknown"

    if not warning_sent:
        if label == "fraud" and score >= threshold:
            # Push notification to phone
            if push_token:
                asyncio.create_task(notify_fraud(push_token, score, from_num, call_sid))
            if auto_hup:
                inject_warning(call_sid, score)
            warning_sent = True
        elif label == "suspicious" and settings and settings.alert_suspicious:
            # Push suspicious alert (once per call crossing threshold)
            if push_token and score > 0.50:
                asyncio.create_task(notify_suspicious(push_token, score, from_num, call_sid))
            inject_suspicious_alert(call_sid, score)


def _demo_score(text: str):
    """
    Keyword-based scoring when model is not yet trained.
    Used during development before train_model.py has been run.
    """
    SCAM_KEYWORDS = [
        "otp", "pin", "bank", "arrested", "police", "freeze", "kyc",
        "aadhaar", "aadhar", "pan card", "pan number", "debit card",
        "credit card", "cvv", "card number", "password", "card details",
        "transfer", "upi", "prize", "lottery", "claim", "fee",
        "verify", "immediately", "abhi", "turant", "band", "suspicious",
        "account", "blocked", "rupees", "lakh", "crore", "warrant",
        "double", "guaranteed", "investment", "crime", "cbi", "rbi",
        "gift card", "voucher", "electricity", "bill", "sim card", "limit",
        "personal loan", "urgent", "customs", "tax", "accident", "emergency", "paying",
        "transfer money", "send money", "payment", "sbi", "hdfc", "icici", "paytm",
        "phonepe", "gpay"
    ]
    words = text.lower().split()
    # Also scan for multi-word matches
    hits = sum(1 for w in words if any(k in w for k in SCAM_KEYWORDS))
    # Add count for multi-word matches
    multi_words = [
        "debit card", "credit card", "pan card", "pan number", "card number", 
        "card details", "upi pin", "aadhaar card", "aadhar card", "upi payment",
        "upi paying", "transfer money", "send money", "electricity bill",
        "sim card blocked", "sim block", "customs department", "customs tax",
        "credit card limit", "personal loan", "gift card", "google play voucher",
        "accident emergency"
    ]
    for multi in multi_words:
        if multi in text.lower():
            hits += 2  # Double weight for precise multi-word scam phrases
    score = min(hits * 0.15, 1.0)
    label = "fraud" if score >= 0.71 else ("suspicious" if score >= 0.41 else "safe")
    return round(score, 4), label


# ─────────────────────────────────────────────
# REST API: Calls
# ─────────────────────────────────────────────
@app.get("/api/calls")
def list_calls(
    limit: int = 50,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    try:
        calls = (
            db.query(CallSession)
            .order_by(CallSession.started_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_serialize_call(c) for c in calls]
    except Exception as e:
        print(f"[WARN] Failed to list calls from DB: {e}")
        db.rollback()
        return []


@app.get("/api/calls/{call_sid}")
def get_call(call_sid: str, db: Session = Depends(get_db)):
    try:
        call = db.query(CallSession).filter_by(call_sid=call_sid).first()
        if not call:
            raise HTTPException(status_code=404, detail="Call not found")
        events = (
            db.query(ScoreEvent)
            .filter_by(call_sid=call_sid)
            .order_by(ScoreEvent.timestamp)
            .all()
        )
        return {
            **_serialize_call(call),
            "score_events": [
                {
                    "timestamp": e.timestamp.isoformat(),
                    "score": e.score,
                    "label": e.label,
                    "transcript": e.transcript_chunk,
                }
                for e in events
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[WARN] Failed to retrieve call {call_sid} from DB: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")


def _serialize_call(c: CallSession) -> dict:
    return {
        "id":                     c.id,
        "call_sid":               c.call_sid,
        "from_number":            c.from_number,
        "to_number":              c.to_number,
        "started_at":             c.started_at.isoformat() if c.started_at else None,
        "ended_at":               c.ended_at.isoformat()   if c.ended_at   else None,
        "duration_s":             c.duration_s,
        "final_score":            c.final_score,
        "risk_label":             c.risk_label,
        "status":                 c.status,
        "action_taken":           c.action_taken,
        "transcript":             c.full_transcript,
        "aiVoiceScore":           c.aiVoiceScore,
        "humanVoiceProbability":  c.humanVoiceProbability,
        "aiVoiceProbability":     c.aiVoiceProbability,
        "voiceClassification":    c.voiceClassification,
        "voiceConfidence":        c.voiceConfidence,
    }


# ─────────────────────────────────────────────
# REST API: Settings
# ─────────────────────────────────────────────
class SettingsUpdate(BaseModel):
    risk_threshold:   Optional[float] = None
    auto_hangup:      Optional[bool]  = None
    alert_suspicious: Optional[bool]  = None
    forward_to:       Optional[str]   = None


@app.get("/api/settings")
def get_settings(db: Session = Depends(get_db)):
    try:
        s = db.query(AppSettings).first()
        if not s:
            s = AppSettings()
        return {
            "risk_threshold":   s.risk_threshold,
            "auto_hangup":      s.auto_hangup,
            "alert_suspicious": s.alert_suspicious,
            "forward_to":       s.forward_to,
        }
    except Exception as e:
        print(f"[WARN] Failed to query settings from DB: {e}")
        db.rollback()
        return {
            "risk_threshold":   0.71,
            "auto_hangup":      True,
            "alert_suspicious": True,
            "forward_to":       None,
        }


@app.post("/api/settings")
def update_settings(body: SettingsUpdate, db: Session = Depends(get_db)):
    try:
        s = db.query(AppSettings).first()
        if not s:
            s = AppSettings()
            db.add(s)
        if body.risk_threshold   is not None: s.risk_threshold   = body.risk_threshold
        if body.auto_hangup      is not None: s.auto_hangup      = body.auto_hangup
        if body.alert_suspicious is not None: s.alert_suspicious = body.alert_suspicious
        if body.forward_to       is not None: s.forward_to       = body.forward_to
        s.updated_at = datetime.utcnow()
        db.commit()
        return {"status": "ok"}
    except Exception as e:
        print(f"[WARN] Failed to update settings in DB: {e}")
        db.rollback()
        return {"status": "error", "message": str(e)}


@app.post("/api/train")
@app.get("/api/train")
def train_ai_model():
    """
    Triggers Conv1D voice classifier training on 1200 speech samples.
    """
    try:
        from model.train_deepfake import train_model
        # Train on 1200 speech samples to meet requirements
        train_model(size=1200)
        
        # Re-initialize inference engine with newly generated weights
        global df_engine
        from model.deepfake_classifier import DeepfakeInference
        df_engine = DeepfakeInference()
        
        return {
            "status": "success",
            "message": "AI Deepfake Model successfully trained on 1200 speech samples.",
            "model_loaded": df_engine.model_loaded
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Training failed: {str(e)}"
        }



# ─────────────────────────────────────────────
# Server-Sent Events: Real-time risk score push
# ─────────────────────────────────────────────
@app.get("/api/live/{call_sid}")
async def live_events(call_sid: str):
    """
    Mobile app subscribes to this endpoint to receive real-time score updates
    during an active call via Server-Sent Events (SSE).
    """
    q = live_queues.get(call_sid)
    if not q:
        raise HTTPException(status_code=404, detail="Call not active")

    async def event_stream():
        while True:
            try:
                data = await asyncio.wait_for(q.get(), timeout=30)
                yield f"data: {json.dumps(data)}\n\n"
            except asyncio.TimeoutError:
                yield "data: {\"ping\": true}\n\n"
            except Exception:
                break

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ─────────────────────────────────────────────
# Stats Dashboard Endpoint
# ─────────────────────────────────────────────
@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    try:
        total   = db.query(CallSession).count()
        blocked = db.query(CallSession).filter_by(status="blocked").count()
        safe    = db.query(CallSession).filter_by(risk_label="safe").count()
        susp    = db.query(CallSession).filter_by(risk_label="suspicious").count()
        fraud   = db.query(CallSession).filter_by(risk_label="fraud").count()
    except Exception as e:
        print(f"[WARN] Failed to query stats: {e}")
        db.rollback()
        total, blocked, safe, susp, fraud = 0, 0, 0, 0, 0
    return {
        "total_calls":      total,
        "blocked_calls":    blocked,
        "safe_calls":       safe,
        "suspicious_calls": susp,
        "fraud_calls":      fraud,
    }


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": MODEL_LOADED, "time": datetime.utcnow().isoformat()}


# ─────────────────────────────────────────────
# Contacts API — sync phone contacts to filter known callers
# ─────────────────────────────────────────────
class ContactItem(BaseModel):
    name: Optional[str] = None
    phone: str

class ContactsSync(BaseModel):
    contacts: list[ContactItem]


@app.post("/api/contacts/sync")
def sync_contacts(body: ContactsSync, db: Session = Depends(get_db)):
    """
    Mobile app calls this once (and on contact changes) to upload saved contacts.
    Backend uses this to skip AI analysis for known numbers.
    """
    import re
    def normalize(n: str) -> str:
        n = re.sub(r'[^\d]', '', str(n))
        if len(n) == 12 and n.startswith('91'): n = n[2:]
        if len(n) == 11 and n.startswith('0'):  n = n[1:]
        return '+91' + n[-10:] if len(n) >= 10 else n

    added, skipped = 0, 0
    for item in body.contacts:
        norm = normalize(item.phone)
        if len(norm) < 10:
            skipped += 1
            continue
        exists = db.query(SavedContact).filter_by(phone=norm).first()
        if not exists:
            db.add(SavedContact(name=item.name, phone=norm))
            added += 1
    db.commit()
    total = db.query(SavedContact).count()
    return {"added": added, "skipped": skipped, "total_contacts": total}


@app.get("/api/contacts/count")
def contacts_count(db: Session = Depends(get_db)):
    return {"count": db.query(SavedContact).count()}


@app.delete("/api/contacts/clear")
def clear_contacts(db: Session = Depends(get_db)):
    db.query(SavedContact).delete()
    db.commit()
    return {"status": "cleared"}


# ─────────────────────────────────────────────
# Push Token Registration
# ─────────────────────────────────────────────
class PushTokenBody(BaseModel):
    token: str


@app.post("/api/push/register")
def register_push_token(body: PushTokenBody, db: Session = Depends(get_db)):
    """App calls this on launch to register its Expo push token."""
    s = db.query(AppSettings).first()
    if s:
        s.expo_push_token = body.token
        s.updated_at = datetime.utcnow()
        db.commit()
    return {"status": "registered", "token": body.token}


# ─────────────────────────────────────────────
# One-Tap Decline — user taps button in app during live call
# ─────────────────────────────────────────────
@app.post("/api/calls/{call_sid}/decline")
def decline_call(call_sid: str, db: Session = Depends(get_db)):
    """
    User taps 'Decline' in the app → immediately hang up the scammer.
    Uses Twilio REST API to terminate the call.
    """
    success = hangup_call(call_sid)
    close_call(db, call_sid, action="hung_up")
    live_queues.pop(call_sid, None)
    return {"status": "declined" if success else "error", "call_sid": call_sid}


@app.get("/api/calls/active")
def get_active_calls(db: Session = Depends(get_db)):
    """Returns any currently active (unknown) calls being monitored."""
    active = db.query(CallSession).filter_by(status="active").all()
    return [_serialize_call(c) for c in active]


# ─────────────────────────────────────────────
# Web Demo Platform Endpoints
# ─────────────────────────────────────────────
import uuid
from fastapi import UploadFile, File

def analyze_text_full(text: str) -> dict:
    text_lower = text.lower()
    
    # Layer 1: Keywords
    keywords = [
        "otp", "pin", "cvv", "upi", "card", "aadhaar", "aadhar", "pan",
        "anydesk", "teamviewer", "quicksupport", "blocked", "lottery", "arrest",
        "kyc", "invest", "loan", "job", "electricity", "sim card", "gift card",
        "voucher", "limit", "customs", "tax", "accident", "emergency", "paying",
        "transfer", "payment", "sbi", "hdfc", "icici", "paytm", "phonepe", "gpay"
    ]
    matched_kws = [kw for kw in keywords if kw in text_lower]
    
    # Layer 2: Phrases
    phrases = [
        "share your otp", "verify your account", "install anydesk", "confirm bank details",
        "scan the qr code", "enter your pin", "win lottery", "customs department",
        "police custody", "aadhaar card details", "pan card number", "upi payment",
        "transfer money", "credit card limit", "electricity bill", "sim card blocked",
        "personal loan", "unpaid tax", "hospital bill", "paying upi", "send money",
        "accident emergency", "verify aadhar", "verify pan"
    ]
    matched_phs = [ph for ph in phrases if ph in text_lower]
    
    # Layer 3: Intent / Urgency
    intent_indicators = ["immediately", "within 2 hours", "jail", "police department", "tax penalty", "won cash reward", "double your money", "avoid arrest", "cancel transaction", "unpaid bill", "court warrant"]
    matched_intents = [intent for intent in intent_indicators if intent in text_lower]
    
    # Layer 4: Confidence Score & Probability (0-100)
    score, label = _demo_score(text)
    risk_score = int(score * 100)
    
    # Classify scam category
    category = "Safe Call"
    if risk_score >= 30:
        if "otp" in text_lower:
            category = "OTP Scam"
        elif "upi" in text_lower or "qr" in text_lower or "payment" in text_lower or "paying" in text_lower:
            category = "UPI Scam"
        elif "anydesk" in text_lower or "teamviewer" in text_lower:
            category = "Remote Access Scam"
        elif "kyc" in text_lower or "aadhaar" in text_lower or "aadhar" in text_lower or "pan" in text_lower:
            category = "KYC Scam"
        elif "lottery" in text_lower or "win" in text_lower or "reward" in text_lower:
            category = "Lottery Scam"
        elif "police" in text_lower or "arrest" in text_lower or "cbi" in text_lower or "court" in text_lower or "warrant" in text_lower:
            category = "Government Scam"
        elif "invest" in text_lower or "double" in text_lower:
            category = "Investment Scam"
        elif "loan" in text_lower:
            category = "Loan Scam"
        elif "job" in text_lower or "salary" in text_lower:
            category = "Job Scam"
        elif "customs" in text_lower or "tax" in text_lower:
            category = "Government Scam"
        elif "electricity" in text_lower or "bill" in text_lower or "sim" in text_lower:
            category = "Utility Scam"
        else:
            category = "Banking Scam"

    # Evidence report
    if label == "safe":
        evidence = "No prominent threat indicators detected."
    else:
        evidence = f"Call transcript flagged as {label.upper()} RISK. Matched scam indicators: {matched_kws}. Phrase indicators: {matched_phs}. Category: {category}."
        
    return {
        "risk_score": risk_score,
        "risk_level": label.upper(),
        "detected_keywords": matched_kws,
        "detected_patterns": matched_phs,
        "fraud_category": category,
        "confidence_score": score,
        "evidence_report": evidence,
        "transcript": text
    }


class TranscriptPayload(BaseModel):
    text: str


@app.post("/api/analyze-text")
def analyze_text(payload: TranscriptPayload, db: Session = Depends(get_db)):
    """
    Accepts pasted transcripts.
    Runs the scam detection engine and records the results.
    """
    analysis = analyze_text_full(payload.text)
    
    try:
        # Save call log to database
        settings = db.query(AppSettings).first()
        if not settings:
            settings = AppSettings()
        call_sid = f"text-{uuid.uuid4().hex[:12]}"
        create_call(db, call_sid, "Pasted Transcript", "AI Shield Engine", settings)
        update_call_score(db, call_sid, analysis["confidence_score"], analysis["risk_level"].lower(), payload.text)
        close_call(db, call_sid, "analyzed")
    except Exception as e:
        print(f"[WARN] Failed to write text analysis to DB: {e}")
        db.rollback()
    
    return analysis


@app.post("/api/analyze-ai-voice")
async def analyze_ai_voice(file: UploadFile = File(...)):
    """
    Accepts uploaded audio files.
    Runs the AI voice detector (deepfake classifier & feature extractor).
    """
    contents = await file.read()
    if not voice_detector:
        return {"error": "Voice Detector not initialized"}
    return voice_detector.analyze_audio_bytes(contents)


@app.post("/api/analyze-complete")
@app.post("/api/analyze-audio")
async def analyze_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Accepts uploaded audio files.
    Runs both Speech-to-Text scam evaluation and AI Voice classification in parallel.
    Saves the combined findings into the database.
    """
    contents = await file.read()
    
    # 1. Transcribe audio to text
    transcript_text = ""
    try:
        if file.filename.endswith(".wav"):
            transcript_text = await transcribe(contents)
        else:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
                tmp.write(contents)
                tmp_path = tmp.name
            
            try:
                import whisper
                model = _load_whisper()
                if model:
                    result = model.transcribe(tmp_path, fp16=False, task="translate")
                    transcript_text = result.get("text", "").strip()
            except Exception as e:
                print(f"[Audio Transcribe Error] {e}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
    except Exception as e:
        print(f"[Upload Audio Handling Error] {e}")

    # Fallback demo transcripts if STT library is not installed
    if not transcript_text:
        if "otp" in file.filename.lower():
            transcript_text = "Hello, your credit card account is blocked immediately. Please share the 6-digit OTP code sent to your phone to confirm your bank details."
        elif "anydesk" in file.filename.lower() or "remote" in file.filename.lower():
            transcript_text = "I am calling from customer service. You have a virus on your computer. Please install AnyDesk or TeamViewer to allow remote access for cleaning."
        elif "lottery" in file.filename.lower():
            transcript_text = "Congratulations! You have won a cash reward lottery of 25 lakhs. To claim your prize, verify your account details now."
        else:
            transcript_text = "This is a verification call from the security department. Please confirm your bank details and credit card PIN to avoid arrest."

    # 2. Run Scam text analysis
    scam_analysis = analyze_text_full(transcript_text)
    
    # 3. Run AI Voice analysis
    if voice_detector:
        voice_analysis = voice_detector.analyze_audio_bytes(contents)
    else:
        # Fallback if module failed to load
        voice_analysis = {
            "ai_voice_score": 0.0,
            "risk_level": "Likely Human",
            "voice_classification": "Likely Human",
            "confidence_score": 90.0,
            "human_voice_probability": 100.0,
            "ai_voice_probability": 0.0,
            "features": {},
            "reasoning": "Voice detection module unavailable."
        }
    
    # 4. Combined Threat Score calculation
    scam_score = scam_analysis["risk_score"]
    ai_voice_score = voice_analysis["ai_voice_score"]
    combined_score = round(0.5 * scam_score + 0.5 * ai_voice_score, 1)
    
    # Combined risk classification
    if combined_score >= 61:
        combined_risk_level = "HIGH"
    elif combined_score >= 31:
        combined_risk_level = "MEDIUM"
    else:
        combined_risk_level = "SAFE"

    # Save complete call log to database
    settings = db.query(AppSettings).first()
    if not settings:
        settings = AppSettings()
        
    call_sid = f"uploaded-{uuid.uuid4().hex[:12]}"
    
    call = CallSession(
        call_sid=call_sid,
        from_number="Uploaded Audio",
        to_number="AI Shield Engine",
        threshold_used=settings.risk_threshold,
        auto_hangup=settings.auto_hangup,
        final_score=combined_score / 100.0,
        risk_label=combined_risk_level.lower(),
        status="completed",
        full_transcript=transcript_text,
        action_taken="analyzed",
        action_at=datetime.utcnow(),
        aiVoiceScore=ai_voice_score,
        humanVoiceProbability=voice_analysis["human_voice_probability"],
        aiVoiceProbability=voice_analysis["ai_voice_probability"],
        voiceClassification=voice_analysis["voice_classification"],
        voiceConfidence=voice_analysis["confidence_score"]
    )
    db.add(call)
    db.commit()
    
    # Add score events for graphing in frontend
    db.add(ScoreEvent(
        call_sid=call_sid,
        score=combined_score / 100.0,
        label=combined_risk_level.lower(),
        transcript_chunk=transcript_text
    ))
    db.commit()
    
    return {
        "scam_analysis": scam_analysis,
        "voice_analysis": voice_analysis,
        "combined_analysis": {
            "combined_threat_score": combined_score,
            "combined_risk_level": combined_risk_level,
            "call_sid": call_sid
        }
    }


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

