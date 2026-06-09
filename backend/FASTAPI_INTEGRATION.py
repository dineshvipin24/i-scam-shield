"""
Integration code to add AI voice detection to your FastAPI backend
Copy and paste this into your backend/main.py
"""

# ============================================================================
# ADD THIS AT THE TOP OF YOUR main.py FILE
# ============================================================================

from backend.model.ai_voice_detector import AIVoiceDetector

# Initialize AI Voice Detector (runs once on startup)
ai_voice_detector = AIVoiceDetector()


# ============================================================================
# ADD THIS ENDPOINT TO YOUR FastAPI APP
# ============================================================================

@app.post("/api/detect-voice")
async def detect_voice(file: UploadFile = File(...)):
    """
    Detect if voice is Human, AI-Generated, or Deepfake
    
    Endpoint: POST /api/detect-voice
    
    Request:
        - file: Audio file (WAV, MP3, OGG, FLAC)
    
    Response:
        {
            "prediction": "Human" | "AI-Generated" | "Deepfake/Synthetic",
            "confidence": 0.0-1.0,
            "probabilities": {
                "human": 0.0-1.0,
                "ai_generated": 0.0-1.0,
                "deepfake_synthetic": 0.0-1.0
            },
            "message": "Analysis complete"
        }
    """
    try:
        # Read audio bytes
        audio_bytes = await file.read()
        
        if not audio_bytes:
            return {"error": "Empty audio file"}, 400
        
        if len(audio_bytes) > 10_000_000:  # 10MB limit
            return {"error": "File too large (max 10MB)"}, 413
        
        # Get prediction
        prediction, probabilities = ai_voice_detector.predict_pcm(audio_bytes)
        
        # Calculate confidence
        confidence = max(probabilities.values())
        
        return {
            "prediction": prediction,
            "confidence": float(confidence),
            "probabilities": {
                "human": float(probabilities["Human"]),
                "ai_generated": float(probabilities["AI-Generated"]),
                "deepfake_synthetic": float(probabilities["Deepfake/Synthetic"])
            },
            "message": "Voice analysis complete"
        }
        
    except Exception as e:
        print(f"Error in voice detection: {e}")
        return {
            "error": str(e),
            "message": "Voice detection failed"
        }, 500


# ============================================================================
# OPTIONAL: Add Health Check Endpoint
# ============================================================================

@app.get("/api/voice-detector-status")
async def voice_detector_status():
    """Check if AI voice detector is ready"""
    return {
        "status": "ready" if ai_voice_detector.model_loaded else "initializing",
        "model_loaded": ai_voice_detector.model_loaded,
        "supported_formats": ["WAV", "MP3", "OGG", "FLAC"]
    }


# ============================================================================
# OPTIONAL: Add Integration with Existing Call Analysis
# ============================================================================

@app.post("/api/analyze-call")
async def analyze_call_with_voice_detection(
    call_id: str,
    caller_number: str,
    file: UploadFile = File(...)
):
    """
    Analyze call combining:
    1. Caller reputation (existing)
    2. Voice authenticity (new)
    3. Deepfake detection (existing)
    """
    try:
        audio_bytes = await file.read()
        
        # 1. Get voice type
        voice_prediction, voice_probs = ai_voice_detector.predict_pcm(audio_bytes)
        
        # 2. Get caller info (from your existing DB)
        caller_info = await get_caller_info(caller_number)
        
        # 3. Combine analysis
        suspicion_score = 0.0
        reasons = []
        
        # Voice analysis
        if voice_prediction == "AI-Generated":
            suspicion_score += 0.4
            reasons.append("AI-generated voice detected")
        elif voice_prediction == "Deepfake/Synthetic":
            suspicion_score += 0.5
            reasons.append("Deepfake/synthetic voice detected")
        
        # Caller reputation
        if caller_info.get("is_blacklisted"):
            suspicion_score += 0.3
            reasons.append("Caller on fraud list")
        
        if caller_info.get("reports_count", 0) > 5:
            suspicion_score += 0.2
            reasons.append(f"Multiple fraud reports ({caller_info['reports_count']})")
        
        is_suspicious = suspicion_score > 0.5
        
        return {
            "call_id": call_id,
            "is_suspicious": is_suspicious,
            "suspicion_score": suspicion_score,
            "voice_type": voice_prediction,
            "voice_confidence": float(max(voice_probs.values())),
            "reasons": reasons,
            "caller_info": {
                "number": caller_number,
                "is_blacklisted": caller_info.get("is_blacklisted", False),
                "reports_count": caller_info.get("reports_count", 0)
            }
        }
        
    except Exception as e:
        print(f"Error in call analysis: {e}")
        return {"error": str(e)}, 500


# ============================================================================
# OPTIONAL: WebSocket for Real-Time Analysis
# ============================================================================

from fastapi import WebSocket

@app.websocket("/ws/voice-detection")
async def websocket_voice_detection(websocket: WebSocket):
    """
    WebSocket endpoint for streaming voice detection
    
    Connect: ws://localhost:8000/ws/voice-detection
    Send: {"audio": base64_encoded_audio}
    Receive: {"prediction": "...", "confidence": ...}
    """
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            
            if "audio" in data:
                import base64
                audio_bytes = base64.b64decode(data["audio"])
                
                prediction, probs = ai_voice_detector.predict_pcm(audio_bytes)
                
                await websocket.send_json({
                    "prediction": prediction,
                    "confidence": float(max(probs.values())),
                    "probabilities": {
                        "human": float(probs["Human"]),
                        "ai_generated": float(probs["AI-Generated"]),
                        "deepfake": float(probs["Deepfake/Synthetic"])
                    }
                })
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()


# ============================================================================
# END OF CODE TO ADD
# ============================================================================
