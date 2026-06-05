"""
push_client.py - Expo Push Notifications
Sends real-time alerts to the user's phone during a live call.
No Firebase/APNs setup needed - uses Expo's free push service.
"""

import os
import httpx

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

async def send_push(
    expo_token: str,
    title: str,
    body: str,
    data: dict = None,
    sound: str = "default",
    priority: str = "high",
):
    """Send a push notification to the user's phone via Expo."""
    if not expo_token or not expo_token.startswith("ExponentPushToken"):
        return False
    payload = {
        "to": expo_token,
        "title": title,
        "body": body,
        "sound": sound,
        "priority": priority,
        "data": data or {},
        "channelId": "scam-alerts",
    }
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.post(EXPO_PUSH_URL, json=payload)
            r.raise_for_status()
            return True
    except Exception as e:
        print(f"[Push] Error: {e}")
        return False


async def notify_suspicious(expo_token: str, score: float, from_number: str, call_sid: str):
    pct = int(score * 100)
    await send_push(
        expo_token,
        title=f"⚠️ Suspicious Call — {pct}% Risk",
        body=f"Unknown caller {from_number} is showing suspicious patterns. Stay alert.",
        data={"type": "suspicious", "call_sid": call_sid, "score": score},
        sound="default",
    )


async def notify_fraud(expo_token: str, score: float, from_number: str, call_sid: str):
    pct = int(score * 100)
    await send_push(
        expo_token,
        title=f"🚨 FRAUD DETECTED — {pct}% Risk",
        body=f"Unknown caller {from_number} is likely a scammer! Tap to decline.",
        data={"type": "fraud", "call_sid": call_sid, "score": score},
        sound="default",
        priority="high",
    )
