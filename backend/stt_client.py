"""
stt_client.py - Speech-to-Text using Deepgram (primary) or Whisper (fallback)
"""

import os
import io
import asyncio
import httpx
from audio_processor import pcm_to_wav_bytes

# ─── Provider selection ───────────────────────────────────────────────────────
STT_PROVIDER = os.getenv("STT_PROVIDER", "deepgram")  # "deepgram" | "whisper"
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")


# ─── Deepgram REST (batch, per audio chunk) ───────────────────────────────────
DEEPGRAM_URL = "https://api.deepgram.com/v1/listen"
DEEPGRAM_PARAMS = {
    "model":       "nova-2",
    "language":    "hi-en",   # Hindi + English code-switching
    "punctuate":   "true",
    "smart_format": "true",
    "encoding":    "linear16",
    "sample_rate": "16000",
}

async def transcribe_deepgram(pcm_bytes: bytes) -> str:
    """Send a PCM buffer to Deepgram and return transcript text."""
    if not DEEPGRAM_API_KEY:
        return ""
    wav_bytes = pcm_to_wav_bytes(pcm_bytes)
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "audio/wav",
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                DEEPGRAM_URL,
                params=DEEPGRAM_PARAMS,
                headers=headers,
                content=wav_bytes,
            )
            resp.raise_for_status()
            data = resp.json()
            alternatives = (
                data.get("results", {})
                    .get("channels", [{}])[0]
                    .get("alternatives", [{}])
            )
            return alternatives[0].get("transcript", "") if alternatives else ""
    except Exception as e:
        print(f"[STT Deepgram Error] {e}")
        return ""


# ─── Local Whisper (fallback, no API key needed) ──────────────────────────────
_whisper_model = None

def _load_whisper():
    global _whisper_model
    if _whisper_model is None:
        try:
            import whisper
            _whisper_model = whisper.load_model("base")
            print("[STT] Whisper model loaded (base)")
        except ImportError:
            print("[STT] Whisper not installed. pip install openai-whisper")
    return _whisper_model


async def translate_text(text: str, source: str = "hi", target: str = "en") -> str:
    """Translate text from Hindi/Hinglish to English using the free MyMemory API."""
    if not text or not text.strip():
        return text
    # Heuristic: skip if it's already plain English/numbers
    import re
    if re.match(r'^[a-zA-Z0-9\s\.,!\?\'\"]+$', text):
        # But if it looks like Hinglish transliteration, we should still translate
        hinglish_words = {"abhi", "turant", "band", "paisa", "rupees", "lakh", "crore", "batao", "karo", "cbi", "police"}
        words = set(text.lower().split())
        if not words.intersection(hinglish_words):
            return text
            
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {"q": text, "langpair": f"{source}|{target}"}
        async with httpx.AsyncClient(timeout=4) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                translated = data.get("responseData", {}).get("translatedText", text)
                # Keep clean text
                return translated
    except Exception as e:
        print(f"[Translate Warning] Failed to translate: {e}")
    return text


async def transcribe_whisper(pcm_bytes: bytes) -> str:
    """Run Whisper inference in a thread pool to translate Hindi/English to English."""
    import tempfile, numpy as np
    loop = asyncio.get_event_loop()

    def _infer():
        model = _load_whisper()
        if model is None:
            return ""
        # Convert PCM bytes to float32 numpy array
        audio = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        # task="translate" translates any spoken language directly into English text
        result = model.transcribe(audio, fp16=False, task="translate")
        return result.get("text", "").strip()

    try:
        return await loop.run_in_executor(None, _infer)
    except Exception as e:
        print(f"[STT Whisper Error] {e}")
        return ""


# ─── Unified interface ────────────────────────────────────────────────────────
async def transcribe(pcm_bytes: bytes) -> str:
    """
    Auto-selects provider based on STT_PROVIDER env var.
    Returns English translation transcript string or empty string on failure.
    """
    if not pcm_bytes:
        return ""
    if STT_PROVIDER == "deepgram" and DEEPGRAM_API_KEY:
        raw_text = await transcribe_deepgram(pcm_bytes)
        return await translate_text(raw_text)
    else:
        return await transcribe_whisper(pcm_bytes)
