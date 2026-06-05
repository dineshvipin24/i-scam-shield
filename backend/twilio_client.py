"""
twilio_client.py - Twilio REST API actions: inject warning, hangup, generate TwiML
"""

import os
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream, Say, Dial


TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN",  "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")
SERVER_URL         = os.getenv("SERVER_URL", "")   # e.g. https://your-ngrok.ngrok.io


def _get_client() -> Client:
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


# ─────────────────────────────────────────────────────────────────────────────
# TwiML Generators
# ─────────────────────────────────────────────────────────────────────────────

def build_incoming_twiml(forward_to: str = None) -> str:
    """
    TwiML returned to Twilio when a call comes in.
    Opens a media stream to our WebSocket AND optionally forwards the call.
    """
    response = VoiceResponse()
    connect = Connect()
    ws_url = f"wss://{SERVER_URL.replace('https://', '').replace('http://', '')}/stream"
    connect.stream(url=ws_url)
    response.append(connect)
    if forward_to:
        response.dial(forward_to)
    else:
        response.say(
            "This call is being protected by AI Scam Shield. "
            "Please hold while we connect you.",
            voice="Polly.Aditi",   # Hindi-accented English voice
            language="en-IN"
        )
    return str(response)


def build_warning_twiml(risk_score: float) -> str:
    """TwiML injected mid-call when fraud is detected."""
    response = VoiceResponse()
    # Play warning beep
    if SERVER_URL:
        response.play(f"{SERVER_URL.rstrip('/')}/static/beep.wav")
    response.say(
        f"Warning! Our AI has detected a high probability of fraud in this call. "
        f"Scam risk score is {int(risk_score * 100)} percent. "
        "Do NOT share any OTP, PIN, or bank details. Disconnecting now.",
        voice="Polly.Aditi",
        language="en-IN"
    )
    response.hangup()
    return str(response)


def build_suspicious_twiml(risk_score: float) -> str:
    """TwiML injected mid-call for suspicious (not yet fraud) calls."""
    response = VoiceResponse()
    # Play warning beep
    if SERVER_URL:
        response.play(f"{SERVER_URL.rstrip('/')}/static/beep.wav")
    response.say(
        f"AI Scam Shield Alert: This call appears suspicious. "
        f"Risk score: {int(risk_score * 100)} percent. "
        "Be cautious. Do not share personal details.",
        voice="Polly.Aditi",
        language="en-IN"
    )
    return str(response)


# ─────────────────────────────────────────────────────────────────────────────
# REST API Actions
# ─────────────────────────────────────────────────────────────────────────────

def inject_warning(call_sid: str, risk_score: float) -> bool:
    """
    Interrupt the live call with a fraud warning and then hang up.
    This is the key power of the cloud bridge architecture.
    """
    try:
        client = _get_client()
        twiml = build_warning_twiml(risk_score)
        client.calls(call_sid).update(twiml=twiml)
        print(f"[Twilio] ⚠️  Warning injected for call {call_sid} (score={risk_score:.2f})")
        return True
    except Exception as e:
        print(f"[Twilio] ERROR injecting warning: {e}")
        return False


def inject_suspicious_alert(call_sid: str, risk_score: float) -> bool:
    """Alert user mid-call without hanging up."""
    try:
        client = _get_client()
        twiml = build_suspicious_twiml(risk_score)
        client.calls(call_sid).update(twiml=twiml)
        print(f"[Twilio] ⚠️  Suspicious alert for call {call_sid} (score={risk_score:.2f})")
        return True
    except Exception as e:
        print(f"[Twilio] ERROR injecting suspicious alert: {e}")
        return False


def hangup_call(call_sid: str) -> bool:
    """Force-terminate a call."""
    try:
        client = _get_client()
        client.calls(call_sid).update(status="completed")
        print(f"[Twilio] 📴 Call {call_sid} terminated")
        return True
    except Exception as e:
        print(f"[Twilio] ERROR hanging up: {e}")
        return False
