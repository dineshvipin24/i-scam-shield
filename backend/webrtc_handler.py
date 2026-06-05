"""
webrtc_handler.py - Handles peer-to-peer WebRTC connections from the Flutter app,
consuming the audio stream for real-time transcription and deepfake voice analysis.
"""

import json
import asyncio
from fastapi import WebSocket
from aiortc import RTCPeerConnection, RTCSessionDescription
import av

# Import backend modules
from database import SessionLocal, create_call, update_call_score, close_call, AppSettings, CallSession
from audio_processor import AudioBuffer
from stt_client import transcribe
from model.deepfake_classifier import DeepfakeInference

# Load Deepfake Inference engine (will run in demo fallback mode if weights are missing)
df_engine = DeepfakeInference()

# Access scam engine from main
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "model"))
from inference import ScamInferenceEngine
scam_engine = ScamInferenceEngine(model_dir=os.path.join(os.path.dirname(__file__), "model"))

async def handle_webrtc_connection(websocket: WebSocket):
    """
    Handles signaling handshake and manages active peer connection.
    Exchanges SDP offer/answers and processes incoming audio tracks.
    """
    pc = RTCPeerConnection()
    db = SessionLocal()
    call_sid = None
    audio_track = None
    
    # Store reference to close properly on connection loss
    active_tasks = []

    try:
        while True:
            # 1. Read message from signaling socket
            message_str = await websocket.receive_text()
            msg = json.loads(message_str)
            event = msg.get("event")

            # ── Call Init ─────────────────────
            if event == "start":
                start_data = msg.get("start", {})
                call_sid = start_data.get("callSid")
                caller_num = start_data.get("callerNumber", "+919876543210")
                
                # Create call record in database
                settings = db.query(AppSettings).first()
                create_call(db, call_sid, caller_num, "webrtc_receiver", settings)
                print(f"[WebRTC Server] 📞 Started call session: {call_sid}")

            # ── SDP Handshake ─────────────────
            elif event == "sdp_offer" and call_sid:
                sdp = msg.get("sdp")
                sdp_type = msg.get("type", "offer")
                
                print(f"[WebRTC Server] Received SDP Offer from Flutter client")
                offer = RTCSessionDescription(sdp=sdp, type=sdp_type)
                
                # Setup incoming track handler
                @pc.on("track")
                def on_track(track):
                    if track.kind == "audio":
                        print("[WebRTC Server] Audio track received. Beginning real-time stream decoding.")
                        nonlocal audio_track
                        audio_track = track
                        # Spawn background task to process stream frames
                        task = asyncio.create_task(
                            _process_webrtc_audio_track(track, websocket, call_sid)
                        )
                        active_tasks.append(task)

                # Exchange descriptions
                await pc.setRemoteDescription(offer)
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)

                # Send answer back to Flutter client
                await websocket.send_text(json.dumps({
                  "event": "sdp_answer",
                  "sdp": pc.localDescription.sdp,
                  "type": pc.localDescription.type
                }))
                print("[WebRTC Server] SDP Answer sent back to client")

            # ── Stop Call ─────────────────────
            elif event == "stop":
                print("[WebRTC Server] Stop event received. Closing connection.")
                break

    except Exception as e:
        print(f"[WebRTC Server Exception] {e}")
    finally:
        # Cleanup
        print("[WebRTC Server] Cleaning up resources...")
        for task in active_tasks:
            task.cancel()
            
        await pc.close()
        if call_sid:
            close_call(db, call_sid, "none")
            
        db.close()


async def _process_webrtc_audio_track(track, websocket: WebSocket, call_sid: str):
    """
    Decodes incoming RTP audio track, converts to linear PCM 16kHz mono,
    and runs transcription and Deepfake algorithms every 1.5 seconds.
    """
    # Resampler to convert input audio formats (e.g. Opus 48kHz) to 16kHz mono PCM
    resampler = av.AudioResampler(
        format="s16",
        layout="mono",
        rate=16000,
    )
    
    audio_buffer = AudioBuffer(buffer_seconds=1.5)
    transcript = []
    
    db = SessionLocal()
    
    try:
        async for frame in track:
            # Resample frame
            resampled_frames = resampler.resample(frame)
            for resampled_frame in resampled_frames:
                # Convert array to raw PCM bytes
                pcm_bytes = resampled_frame.to_ndarray().tobytes()
                # Push into buffer (returns True when 1.5 seconds accumulated)
                is_ready = audio_buffer.push_raw_pcm(pcm_bytes)
                
                if is_ready:
                    chunk = audio_buffer.flush()
                    # Run Deepfake voice classification and Speech-to-Text translation
                    asyncio.create_task(
                        _score_chunk(chunk, websocket, call_sid, transcript, db)
                    )
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"[WebRTC Track Processing Error] {e}")
    finally:
        db.close()


async def _score_chunk(pcm_bytes: bytes, websocket: WebSocket, call_sid: str, transcript: list, db):
    """STT transcription, scam classification, deepfake classification."""
    try:
        # 1. Run Speech-to-Text translation (English only)
        text = await transcribe(pcm_bytes)
        
        # 2. Run Deepfake Classifier
        df_score = df_engine.predict_pcm(pcm_bytes)
        is_deepfake = df_score > 0.50

        if text:
            transcript.append(text)
            if len(transcript) > 20:
                transcript.pop(0)
            rolling_text = " ".join(transcript)
            
            # Predict Scam
            score, label = scam_engine.predict_rolling(rolling_text)
        else:
            # Keep existing scores
            score, label = 0.0, "safe"
            
        print(f"[WebRTC AI] call={call_sid} | Scam={score:.2f} ({label}) | Deepfake={df_score:.2f} (AI={is_deepfake}) | Text: '{text}'")

        # 3. Update database
        update_call_score(db, call_sid, score, label, text)

        # 4. Push updates to Flutter client via signaling WebSocket
        await websocket.send_text(json.dumps({
            "event": "call_update",
            "data": {
                "score": score,
                "label": label,
                "transcript": text,
                "deepfake_score": df_score,
                "is_deepfake": is_deepfake
            }
        }))
        
    except Exception as e:
        print(f"[WebRTC Chunk Scoring Error] {e}")
