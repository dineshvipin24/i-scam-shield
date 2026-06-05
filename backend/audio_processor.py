"""
audio_processor.py - Decode Twilio's mu-law base64 audio and buffer it
"""

import audioop
import base64
import struct
from collections import deque


TWILIO_SAMPLE_RATE = 8000    # Hz (mu-law)
TARGET_SAMPLE_RATE = 16000   # Hz (Whisper/Deepgram prefer 16kHz)
CHUNK_DURATION_MS  = 20      # ms per Twilio chunk
BUFFER_DURATION_S  = 1.5     # seconds to buffer before sending to STT


class AudioBuffer:
    """
    Accumulates raw PCM bytes from Twilio's μ-law stream.
    Call push_chunk() for each incoming WebSocket message.
    Call flush() to get a PCM frame ready for STT.
    """

    def __init__(self, buffer_seconds: float = BUFFER_DURATION_S):
        self._buffer = bytearray()
        self._target_bytes = int(TARGET_SAMPLE_RATE * 2 * buffer_seconds)  # 16-bit PCM

    def push_chunk(self, payload_b64: str) -> bool:
        """
        Decode base64 mu-law → upsample to 16kHz PCM → append to buffer.
        Returns True when the buffer is full and ready to flush.
        """
        try:
            mulaw_bytes = base64.b64decode(payload_b64)
            # μ-law → linear 16-bit PCM at 8kHz
            pcm_8k = audioop.ulaw2lin(mulaw_bytes, 2)
            # Upsample 8kHz → 16kHz
            pcm_16k, _ = audioop.ratecv(pcm_8k, 2, 1, TWILIO_SAMPLE_RATE,
                                         TARGET_SAMPLE_RATE, None)
            self._buffer.extend(pcm_16k)
        except Exception:
            pass

        return len(self._buffer) >= self._target_bytes

    def push_raw_pcm(self, pcm_16k_bytes: bytes) -> bool:
        """Append raw 16kHz PCM bytes directly to the buffer."""
        self._buffer.extend(pcm_16k_bytes)
        return len(self._buffer) >= self._target_bytes

    def flush(self) -> bytes:
        """Return all buffered PCM bytes and clear the buffer."""
        data = bytes(self._buffer)
        self._buffer.clear()
        return data

    def is_ready(self) -> bool:
        return len(self._buffer) >= self._target_bytes

    def clear(self):
        self._buffer.clear()


def pcm_to_wav_bytes(pcm_bytes: bytes,
                      sample_rate: int = TARGET_SAMPLE_RATE,
                      channels: int = 1,
                      sample_width: int = 2) -> bytes:
    """Wrap raw PCM in a minimal WAV header for STT APIs that require it."""
    data_size = len(pcm_bytes)
    header = struct.pack(
        "<4sI4s4sIHHIIHH4sI",
        b"RIFF",
        36 + data_size,
        b"WAVE",
        b"fmt ",
        16,               # chunk size
        1,                # PCM
        channels,
        sample_rate,
        sample_rate * channels * sample_width,
        channels * sample_width,
        sample_width * 8,
        b"data",
        data_size,
    )
    return header + pcm_bytes
