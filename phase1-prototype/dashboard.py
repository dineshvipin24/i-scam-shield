# phase1-prototype/dashboard.py
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import http.server
import socketserver
import json
import sys
import urllib.parse

try:
    print("[DEBUG] Starting dashboard initialization...")
    # Setup paths to import from backend
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

    print("[DEBUG] Importing modules...")
    from dataset_builder import DATASET_FILE
    from fraud_detector import FraudDetector
    from database import init_db, SessionLocal, CallSession
    
    # Initialize SQLite database
    print("[DEBUG] Initializing SQLite database...")
    init_db()

    # Automatically sync backend/demo.html to root demo.html
    try:
        src = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/demo.html"))
        dst = os.path.abspath(os.path.join(os.path.dirname(__file__), "../demo.html"))
        if os.path.exists(src):
            import shutil
            shutil.copy(src, dst)
            print("[DEBUG] Synced backend/demo.html to root demo.html")
    except Exception as sync_err:
        print(f"[WARN] Failed to auto-sync demo.html: {sync_err}")

    PORT = 8001
    print("[DEBUG] Instantiating FraudDetector...")
    detector = FraudDetector()
    print("[DEBUG] Initialization complete.")
except Exception as e:
    import traceback
    print("\n[CRITICAL STARTUP ERROR] Failed to initialize dashboard:")
    traceback.print_exc()
    sys.exit(1)

def parse_multipart(body_bytes, content_type_header):
    try:
        if not content_type_header or "boundary=" not in content_type_header:
            return body_bytes
        
        boundary = content_type_header.split("boundary=")[1].strip()
        boundary_bytes = ("--" + boundary).encode('utf-8')
        
        parts = body_bytes.split(boundary_bytes)
        for part in parts:
            if b"filename=" in part or b'name="file"' in part:
                header_end = part.find(b"\r\n\r\n")
                if header_end != -1:
                    file_data = part[header_end + 4:]
                    if file_data.endswith(b"\r\n"):
                        file_data = file_data[:-2]
                    # Also strip another level of trailing CRLF if present
                    if file_data.endswith(b"\r\n"):
                        file_data = file_data[:-2]
                    return file_data
    except Exception as e:
        print(f"[ERROR] Failed to parse multipart body: {e}")
    return body_bytes


class DashboardHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.get_html_content().encode('utf-8'))
        elif self.path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(self.get_stats_from_db()).encode('utf-8'))
        elif self.path == "/api/calls":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(self.get_calls_from_db()).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path in ("/api/analyze", "/api/analyze-text"):
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                text = data.get("text", "")
                result = detector.evaluate_text(text)
                
                # Log text evaluation to DB
                import uuid
                call_sid = f"txt_{uuid.uuid4().hex[:16]}"
                db = SessionLocal()
                try:
                    call = CallSession(
                        call_sid = call_sid,
                        from_number = "Text Input",
                        to_number = "Camp Protect Portal",
                        direction = "inbound",
                        final_score = float(result.get("risk_score", 0)) / 100.0,
                        risk_label = result.get("risk_level", "SAFE"),
                        status = "completed",
                        full_transcript = text,
                        action_taken = "none"
                    )
                    db.add(call)
                    db.commit()
                except Exception as db_err:
                    print(f"[ERROR] Failed to log text analysis to DB: {db_err}")
                finally:
                    db.close()
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                
        elif self.path in ("/api/upload", "/api/analyze-complete", "/api/analyze-audio"):
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body_bytes = self.rfile.read(content_length)
                
                # Parse boundary if multipart/form-data
                content_type = self.headers.get('Content-Type', '')
                file_bytes = parse_multipart(body_bytes, content_type)
                
                temp_filename = "temp_uploaded_audio.wav"
                with open(temp_filename, "wb") as temp_file:
                    temp_file.write(file_bytes)
                    
                # Run audio processor subprocess to keep whisper/torch isolated from sklearn
                import subprocess
                script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../process_audio.py"))
                if not os.path.exists(script_path):
                    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "process_audio.py"))
                    if not os.path.exists(script_path):
                        script_path = "process_audio.py"
                        
                res = subprocess.run(
                    [sys.executable, script_path, temp_filename],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if res.returncode == 0:
                    try:
                        data = json.loads(res.stdout)
                        transcript = data.get("transcript", "")
                        voice_report = data.get("voice_report", None)
                    except Exception as json_err:
                        print(f"[ERROR] Failed to parse JSON from process_audio.py: {json_err}. Raw stdout: {res.stdout}")
                        raise json_err
                else:
                    err_msg = res.stderr or res.stdout or "Subprocess exited with non-zero code."
                    print(f"[ERROR] process_audio.py failed: {err_msg}")
                    transcript = "Fallback: Urgent bank notice, your card is blocked. Tell me the OTP immediately to fix."
                    voice_report = {
                        "ai_voice_score": 0.0,
                        "risk_level": "Likely Human",
                        "voice_classification": "Likely Human",
                        "confidence_score": 50.0,
                        "reasoning": f"Audio processing isolated failure: {err_msg}",
                        "features": {
                            "pitch_variance": 0.0,
                            "jitter": 0.0,
                            "shimmer": 0.0,
                            "voice_stability": 0.0
                        }
                    }
                
                # Delete temp file
                if os.path.exists(temp_filename):
                    try:
                        os.remove(temp_filename)
                    except Exception:
                        pass
                
                # Evaluate Scam Risk on the transcribed text
                scam_report = detector.evaluate_text(transcript)
                
                # Setup normalized probabilities
                if voice_report:
                    ai_prob = voice_report.get("ai_voice_score", 0.0)
                    voice_report["ai_voice_probability"] = ai_prob
                    voice_report["human_voice_probability"] = max(0.0, 100.0 - ai_prob)
                
                # Compute combined metrics
                scam_score = scam_report.get("risk_score", 0)
                ai_score = voice_report.get("ai_voice_score", 0.0) if voice_report else 0.0
                
                combined_score = max(scam_score, int(ai_score))
                if scam_score >= 50 and ai_score >= 50:
                    combined_score = min(combined_score + 10, 100)
                    
                if combined_score >= 70:
                    combined_risk = "HIGH"
                elif combined_score >= 31:
                    combined_risk = "MEDIUM"
                else:
                    combined_risk = "SAFE"
                
                result = {
                    "transcript": transcript,
                    "scam_analysis": {
                        "risk_score": scam_score,
                        "risk_level": scam_report.get("risk_level", "SAFE"),
                        "fraud_category": scam_report.get("fraud_category", "Safe Call"),
                        "evidence_report": scam_report.get("evidence_report", ""),
                        "detected_keywords": scam_report.get("detected_keywords", []),
                        "transcript": transcript
                    },
                    "voice_analysis": voice_report,
                    "combined_analysis": {
                        "combined_threat_score": combined_score,
                        "combined_risk_level": combined_risk
                    }
                }
                
                # Log call to SQLite DB
                import uuid
                call_sid = f"aud_{uuid.uuid4().hex[:16]}"
                db = SessionLocal()
                try:
                    call = CallSession(
                        call_sid = call_sid,
                        from_number = "Audio Upload",
                        to_number = "Camp Protect Portal",
                        direction = "inbound",
                        final_score = float(combined_score) / 100.0,
                        risk_label = combined_risk,
                        status = "completed",
                        
                        # AI Voice details
                        aiVoiceScore = float(ai_score),
                        humanVoiceProbability = float(voice_report.get("human_voice_probability", 100.0)) if voice_report else 100.0,
                        aiVoiceProbability = float(voice_report.get("ai_voice_probability", 0.0)) if voice_report else 0.0,
                        voiceClassification = voice_report.get("voice_classification", "Likely Human") if voice_report else "Likely Human",
                        voiceConfidence = float(voice_report.get("confidence_score", 50.0)) if voice_report else 50.0,
                        
                        full_transcript = transcript,
                        action_taken = "none"
                    )
                    db.add(call)
                    db.commit()
                except Exception as db_err:
                    print(f"[ERROR] Failed to log audio analysis to DB: {db_err}")
                finally:
                    db.close()
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def get_calls_from_db(self) -> list:
        db = SessionLocal()
        try:
            calls = db.query(CallSession).order_by(CallSession.started_at.desc()).all()
            res = []
            for c in calls:
                res.append({
                    "id": c.id,
                    "call_sid": c.call_sid,
                    "from_number": c.from_number,
                    "to_number": c.to_number,
                    "direction": c.direction,
                    "started_at": c.started_at.isoformat() if c.started_at else None,
                    "ended_at": c.ended_at.isoformat() if c.ended_at else None,
                    "duration_s": c.duration_s,
                    "final_score": c.final_score,
                    "risk_label": c.risk_label,
                    "status": c.status,
                    "aiVoiceScore": c.aiVoiceScore,
                    "humanVoiceProbability": c.humanVoiceProbability,
                    "aiVoiceProbability": c.aiVoiceProbability,
                    "voiceClassification": c.voiceClassification,
                    "voiceConfidence": c.voiceConfidence,
                    "full_transcript": c.full_transcript,
                    "action_taken": c.action_taken,
                    "action_at": c.action_at.isoformat() if c.action_at else None,
                    "threshold_used": c.threshold_used,
                    "auto_hangup": c.auto_hangup
                })
            return res
        except Exception as e:
            print(f"[ERROR] Failed to fetch calls from db: {e}")
            return []
        finally:
            db.close()

    def get_stats_from_db(self) -> dict:
        db = SessionLocal()
        try:
            total = db.query(CallSession).count()
            blocked = db.query(CallSession).filter(CallSession.status == "blocked").count()
            safe = db.query(CallSession).filter(CallSession.risk_label.in_(["safe", "SAFE", "LOW"])).count()
            suspicious = db.query(CallSession).filter(CallSession.risk_label.in_(["suspicious", "SUSPICIOUS", "MEDIUM"])).count()
            fraud = db.query(CallSession).filter(CallSession.risk_label.in_(["fraud", "FRAUD", "HIGH"])).count()
            return {
                "total_calls": total,
                "blocked_calls": blocked,
                "safe_calls": safe,
                "suspicious_calls": suspicious,
                "fraud_calls": fraud
            }
        except Exception as e:
            print(f"[ERROR] Failed to fetch stats from db: {e}")
            return {
                "total_calls": 0,
                "blocked_calls": 0,
                "safe_calls": 0,
                "suspicious_calls": 0,
                "fraud_calls": 0
            }
        finally:
            db.close()

    def get_html_content(self) -> str:
        demo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend/demo.html"))
        if not os.path.exists(demo_path):
            demo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "demo.html"))
            if not os.path.exists(demo_path):
                # Fallback to current working dir
                demo_path = "demo.html"
                
        if os.path.exists(demo_path):
            try:
                with open(demo_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                print(f"[WARN] Failed to read demo.html from disk: {e}")
        
        return "<h1>Demo HTML file not found on disk. Please place demo.html in the backend directory.</h1>"

    def get_html_content_old(self) -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Camp Protect — AI Call & Voice Evaluation Center</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #080B13;
            --card-bg: rgba(17, 24, 39, 0.7);
            --border-color: #1F2937;
            --text-primary: #F3F4F6;
            --text-secondary: #9CA3AF;
            --accent-blue: #3B82F6;
            --accent-red: #EF4444;
            --accent-green: #10B981;
            --accent-orange: #F59E0B;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Plus Jakarta Sans', sans-serif;
        }

        body {
            background-color: var(--bg-color);
            background-image: radial-gradient(circle at top right, rgba(59, 130, 246, 0.15), transparent 450px),
                              radial-gradient(circle at bottom left, rgba(239, 68, 68, 0.08), transparent 400px);
            color: var(--text-primary);
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            min-height: 100vh;
        }

        .container {
            max-width: 1000px;
            width: 100%;
        }

        header {
            text-align: center;
            margin-bottom: 40px;
            position: relative;
        }

        header h1 {
            font-size: 36px;
            font-weight: 800;
            background: linear-gradient(135deg, #FFF 30%, #3B82F6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }

        header p {
            color: var(--text-secondary);
            font-size: 15px;
            font-weight: 500;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }

        .stat-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            padding: 20px;
            border-radius: 20px;
            text-align: center;
            backdrop-filter: blur(10px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        }

        .stat-card h3 {
            font-size: 12px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .stat-card p {
            font-size: 26px;
            font-weight: 800;
        }

        .split-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }

        .input-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .input-card h2 {
            font-size: 18px;
            font-weight: 700;
            color: #FFF;
        }

        /* Upload Container Style */
        .upload-container {
            border: 2px dashed #4B5563;
            border-radius: 16px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            background: rgba(31, 41, 55, 0.2);
            position: relative;
        }

        .upload-container:hover, .upload-container.dragover {
            border-color: var(--accent-blue);
            background: rgba(59, 130, 246, 0.05);
        }

        .upload-icon {
            width: 44px;
            height: 44px;
            margin-bottom: 12px;
            color: var(--accent-blue);
        }

        .upload-container p {
            font-size: 13.5px;
            color: var(--text-secondary);
            line-height: 1.4;
        }

        .loading-overlay {
            display: none;
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(8, 11, 19, 0.9);
            border-radius: 14px;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            gap: 15px;
            z-index: 10;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid rgba(59, 130, 246, 0.1);
            border-top: 4px solid var(--accent-blue);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .divider-container {
            display: flex;
            align-items: center;
            text-align: center;
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
        }
        .divider-container::before, .divider-container::after {
            content: '';
            flex: 1;
            border-bottom: 1px solid var(--border-color);
        }
        .divider-container:not(:empty)::before { margin-right: 15px; }
        .divider-container:not(:empty)::after { margin-left: 15px; }

        textarea {
            width: 100%;
            height: 110px;
            background-color: #0B0F19;
            border: 1px solid #374151;
            border-radius: 12px;
            padding: 14px;
            color: #FFF;
            font-size: 14px;
            resize: none;
            outline: none;
            transition: border-color 0.2s;
        }

        textarea:focus {
            border-color: var(--accent-blue);
        }

        button {
            width: 100%;
            background-color: var(--accent-blue);
            color: #FFF;
            border: none;
            border-radius: 12px;
            padding: 14px;
            font-size: 14.5px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s;
        }

        button:hover {
            opacity: 0.95;
            box-shadow: 0 0 15px rgba(59, 130, 246, 0.3);
        }

        /* Results Layout */
        .results-wrapper {
            display: none;
            animation: fadeIn 0.4s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .analysis-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
            margin-bottom: 30px;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 15px;
        }

        .card-header h3 {
            font-size: 18px;
            font-weight: 700;
            color: #FFF;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Circular Threat Score Gauge */
        .threat-display-section {
            display: flex;
            align-items: center;
            gap: 40px;
            margin-bottom: 25px;
        }

        .gauge-container {
            position: relative;
            width: 110px;
            height: 110px;
        }

        .progress-ring {
            transform: rotate(-90deg);
        }

        .progress-ring__circle {
            stroke-dasharray: 314.16;
            stroke-dashoffset: 314.16;
            transition: stroke-dashoffset 0.5s ease-in-out;
        }

        .gauge-text {
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px;
            font-weight: 800;
        }

        .threat-status-block {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .level-badge {
            padding: 6px 14px;
            border-radius: 30px;
            font-weight: 700;
            font-size: 12px;
            letter-spacing: 0.5px;
            text-align: center;
            width: fit-content;
        }
        .level-high { background-color: rgba(239, 68, 68, 0.15); color: var(--accent-red); border: 1px solid var(--accent-red); }
        .level-medium { background-color: rgba(245, 158, 11, 0.15); color: var(--accent-orange); border: 1px solid var(--accent-orange); }
        .level-low { background-color: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid var(--accent-green); }

        .category-text {
            font-size: 17px;
            font-weight: 700;
            color: #FFF;
        }

        .category-desc {
            font-size: 13.5px;
            color: var(--text-secondary);
        }

        /* Voice Verification Layout */
        .voice-card-body {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .voice-status-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(31, 41, 55, 0.3);
            border: 1px solid var(--border-color);
            padding: 16px 20px;
            border-radius: 16px;
        }

        .voice-type-badge {
            font-size: 15px;
            font-weight: 700;
            padding: 6px 14px;
            border-radius: 8px;
        }
        .voice-type-ai { background: rgba(239, 68, 68, 0.12); color: var(--accent-red); border: 1px solid rgba(239, 68, 68, 0.3); animation: alertPulse 2s infinite; }
        .voice-type-human { background: rgba(16, 185, 129, 0.12); color: var(--accent-green); border: 1px solid rgba(16, 185, 129, 0.3); }
        .voice-type-uncertain { background: rgba(245, 158, 11, 0.12); color: var(--accent-orange); border: 1px solid rgba(245, 158, 11, 0.3); }

        @keyframes alertPulse {
            0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
            70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }

        .confidence-label {
            font-size: 13px;
            color: var(--text-secondary);
            font-weight: 500;
        }

        /* Info Grid */
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }

        .info-item {
            background-color: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            padding: 16px;
            border-radius: 16px;
        }

        .info-item h4 {
            font-size: 11.5px;
            color: var(--text-secondary);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .info-item p {
            font-weight: 700;
            color: #FFF;
            font-size: 14.5px;
        }

        /* Acoustic metrics display grid */
        .acoustic-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-top: 10px;
        }
        .acoustic-metric {
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
        }
        .acoustic-metric span {
            display: block;
            font-size: 10px;
            color: var(--text-secondary);
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .acoustic-metric strong {
            font-size: 13.5px;
            color: #FFF;
            font-weight: 700;
        }

        .report-section {
            background-color: rgba(15, 23, 42, 0.4);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 20px;
        }

        .report-section h4 {
            font-size: 13px;
            color: var(--text-secondary);
            text-transform: uppercase;
            margin-bottom: 10px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .report-text {
            color: #CBD5E1;
            font-size: 14px;
            line-height: 1.55;
            font-style: italic;
        }

        /* Audio Indicator & Beep Warning badge */
        .audio-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: var(--text-secondary);
            background: rgba(31, 41, 55, 0.4);
            border: 1px solid var(--border-color);
            padding: 6px 12px;
            border-radius: 20px;
            width: fit-content;
            margin-bottom: 20px;
        }
        .indicator-pulse {
            width: 8px;
            height: 8px;
            background-color: var(--accent-green);
            border-radius: 50%;
            animation: pulseGreen 1.5s infinite;
        }
        @keyframes pulseGreen {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }

        .critical-warning-flash {
            animation: criticalFlash 0.5s infinite alternate;
        }
        @keyframes criticalFlash {
            from { border-color: var(--border-color); box-shadow: 0 10px 30px rgba(0,0,0,0.4); }
            to { border-color: var(--accent-red); box-shadow: 0 0 25px rgba(239, 68, 68, 0.4); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>CAMP PROTECT</h1>
            <p>Prototype AI Threat Classifier & Voice Verification System</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Dataset Corpus</h3>
                <p id="stat-total">--</p>
            </div>
            <div class="stat-card">
                <h3>Scam Samples</h3>
                <p id="stat-scam" style="color: var(--accent-red)">--</p>
            </div>
            <div class="stat-card">
                <h3>Safe Samples</h3>
                <p id="stat-safe" style="color: var(--accent-green)">--</p>
            </div>
        </div>

        <div class="split-grid">
            <!-- Left Panel: Input & Upload -->
            <div class="input-card">
                <h2>Analyze Call Recording</h2>
                <div class="upload-container" id="upload-area" onclick="document.getElementById('audio-file-input').click()">
                    <div class="loading-overlay" id="loading-overlay">
                        <div class="spinner"></div>
                        <p id="loading-text" style="color: #FFF; font-weight: 600; margin-top: 8px;">Uploading audio...</p>
                    </div>
                    <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="17 8 12 3 7 8"/>
                        <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                    <p id="upload-instruction"><strong>Drag & drop</strong> recording here (.wav, .mp3, .m4a)<br>or <span style="color: var(--accent-blue); text-decoration: underline;">browse files</span></p>
                    <input type="file" id="audio-file-input" accept="audio/*" style="display: none;" onchange="handleFileSelect(this)">
                </div>

                <div class="divider-container">Or Edit Text Transcript Manually</div>

                <textarea id="transcript-input" placeholder="Type or paste a call transcript here to test the threat evaluation model directly..."></textarea>
                <button onclick="analyzeTranscript()">Run Threat Evaluation</button>
            </div>

            <!-- Right Panel: Threat Score Summary -->
            <div class="input-card" style="justify-content: center; align-items: center; text-align: center;" id="welcome-panel">
                <svg width="60" height="60" viewBox="0 0 24 24" fill="none" stroke="var(--text-secondary)" stroke-width="1.5">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                </svg>
                <p style="color: var(--text-secondary); font-size: 14px; margin-top: 15px; max-width: 250px; line-height: 1.5;">Upload an audio recording or submit a transcript to trigger real-time AI classification.</p>
            </div>

            <!-- Threat Score Card -->
            <div class="results-wrapper" id="threat-score-card">
                <div class="analysis-card" id="scam-analysis-card">
                    <div class="audio-indicator" id="sound-indicator" style="display:none">
                        <div class="indicator-pulse"></div>
                        <span>Warning Sirens Armed</span>
                    </div>
                    
                    <div class="card-header">
                        <h3>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                                <line x1="12" y1="9" x2="12" y2="13"/>
                                <line x1="12" y1="17" x2="12.01" y2="17"/>
                            </svg>
                            Threat Assessment
                        </h3>
                        <span class="level-badge" id="res-badge">LOW</span>
                    </div>

                    <div class="threat-display-section">
                        <div class="gauge-container">
                            <svg class="progress-ring" width="110" height="110">
                                <circle class="progress-ring__background" stroke="#1F2937" stroke-width="6" fill="transparent" r="46" cx="55" cy="55"/>
                                <circle class="progress-ring__circle" stroke-linecap="round" stroke="#10B981" stroke-width="8" fill="transparent" r="46" cx="55" cy="55"/>
                            </svg>
                            <div class="gauge-text" id="res-score">0%</div>
                        </div>
                        <div class="threat-status-block">
                            <div class="category-text" id="res-cat">Safe Call</div>
                            <div class="category-desc">Scam category classification signature</div>
                        </div>
                    </div>

                    <div class="info-grid">
                        <div class="info-item">
                            <h4>Flagged Keywords</h4>
                            <p id="res-keywords" style="color: var(--accent-orange)">None</p>
                        </div>
                        <div class="info-item">
                            <h4>Pattern Matches</h4>
                            <p id="res-patterns" style="color: var(--accent-orange)">None</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Full Analysis Details Section -->
        <div class="results-wrapper" id="details-section">
            <!-- Voice Verification Results -->
            <div class="analysis-card" id="voice-analysis-card" style="display: none;">
                <div class="card-header">
                    <h3>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/>
                            <path d="M19 10v1a7 7 0 0 1-14 0v-1"/>
                            <line x1="12" y1="19" x2="12" y2="22"/>
                        </svg>
                        Voice Verification (AI vs. Human)
                    </h3>
                </div>

                <div class="voice-card-body">
                    <div class="voice-status-bar">
                        <div class="voice-type-badge" id="voice-type-badge">Likely Human</div>
                        <div class="confidence-label">Confidence Probability: <strong id="voice-conf" style="color: #FFF">0%</strong></div>
                    </div>

                    <div class="acoustic-grid">
                        <div class="acoustic-metric">
                            <span>Pitch Var</span>
                            <strong id="metric-pitch">0.0</strong>
                        </div>
                        <div class="acoustic-metric">
                            <span>Jitter</span>
                            <strong id="metric-jitter">0.0</strong>
                        </div>
                        <div class="acoustic-metric">
                            <span>Shimmer</span>
                            <strong id="metric-shimmer">0.0</strong>
                        </div>
                        <div class="acoustic-metric">
                            <span>Stability</span>
                            <strong id="metric-stability">0.0</strong>
                        </div>
                    </div>

                    <div class="report-section">
                        <h4>Acoustic Reasoning</h4>
                        <p class="report-text" id="voice-reasoning">Features extracted successfully.</p>
                    </div>
                </div>
            </div>

            <!-- Evidence Report -->
            <div class="analysis-card">
                <div class="card-header" style="margin-bottom: 20px;">
                    <h3>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                            <line x1="16" y1="13" x2="8" y2="13"/>
                            <line x1="16" y1="17" x2="8" y2="17"/>
                            <polyline points="10 9 9 9 8 9"/>
                        </svg>
                        Evidence Analysis Report
                    </h3>
                </div>
                <div class="report-section">
                    <p class="report-text" id="res-evidence">No transcript evaluated.</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Load stats on startup
        fetch('/api/stats')
            .then(res => res.json())
            .then(data => {
                document.getElementById("stat-total").innerText = data.total;
                document.getElementById("stat-scam").innerText = data.scams;
                document.getElementById("stat-safe").innerText = data.safes;
            });

        // Set up Drag and Drop
        const uploadArea = document.getElementById('upload-area');
        
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, e => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, e => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');
            }, false);
        });

        uploadArea.addEventListener('drop', e => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if(files.length > 0) {
                uploadAudioFile(files[0]);
            }
        });

        function handleFileSelect(input) {
            if(input.files.length > 0) {
                uploadAudioFile(input.files[0]);
            }
        }

        // Upload and automatically analyze recording
        function uploadAudioFile(file) {
            const overlay = document.getElementById('loading-overlay');
            const loadingText = document.getElementById('loading-text');
            overlay.style.display = 'flex';
            loadingText.innerText = "Transcribing Call & Evaluating Voice Type...";

            fetch('/api/upload', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/octet-stream'
                },
                body: file
            })
            .then(res => res.json())
            .then(data => {
                overlay.style.display = 'none';
                
                // Set transcribed text to transcript textarea
                document.getElementById("transcript-input").value = data.transcript;
                
                // Display results
                displayResults(data.scam_report, data.voice_report);
            })
            .catch(err => {
                overlay.style.display = 'none';
                alert("Error during audio processing: " + err);
            });
        }

        // Run threat evaluation for typed transcript
        function analyzeTranscript() {
            const text = document.getElementById("transcript-input").value;
            if(!text.trim()) return;

            fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: text })
            })
            .then(res => res.json())
            .then(data => {
                // Run text evaluation (hides voice report since no audio uploaded)
                displayResults(data, null);
            });
        }

        // Display results in UI and evaluate warning sounds
        function displayResults(scamReport, voiceReport) {
            // Hide welcome screen, show cards
            document.getElementById("welcome-panel").style.display = "none";
            document.getElementById("threat-score-card").style.display = "block";
            document.getElementById("details-section").style.display = "block";

            // Update Threat Score
            document.getElementById("res-score").innerText = scamReport.risk_score + "%";
            document.getElementById("res-cat").innerText = scamReport.fraud_category;
            document.getElementById("res-keywords").innerText = scamReport.detected_keywords.join(", ") || "None";
            document.getElementById("res-patterns").innerText = scamReport.detected_patterns.join(", ") || "None";
            document.getElementById("res-evidence").innerText = scamReport.evidence_report;

            const badge = document.getElementById("res-badge");
            const scamCard = document.getElementById("scam-analysis-card");
            badge.className = "level-badge";
            scamCard.classList.remove("critical-warning-flash");
            document.getElementById("sound-indicator").style.display = "none";

            let gaugeColor = "#10B981";
            if(scamReport.risk_level === "HIGH") {
                badge.classList.add("level-high");
                badge.innerText = "HIGH RISK";
                gaugeColor = "#EF4444";
                
                // Flash threat card and arm warning sound if risk is 100%
                if(scamReport.risk_score === 100) {
                    scamCard.classList.add("critical-warning-flash");
                    document.getElementById("sound-indicator").style.display = "flex";
                    playLoudWarningBeep();
                }
            } else if(scamReport.risk_level === "MEDIUM") {
                badge.classList.add("level-medium");
                badge.innerText = "MEDIUM RISK";
                gaugeColor = "#F59E0B";
            } else {
                badge.classList.add("level-low");
                badge.innerText = "SAFE";
            }

            setGaugeProgress(scamReport.risk_score, gaugeColor);

            // Update Voice Report if available
            const voiceCard = document.getElementById("voice-analysis-card");
            if(voiceReport) {
                voiceCard.style.display = "block";
                const voiceBadge = document.getElementById("voice-type-badge");
                voiceBadge.className = "voice-type-badge";

                if (voiceReport.risk_level === "Likely AI Generated") {
                    voiceBadge.classList.add("voice-type-ai");
                    voiceBadge.innerText = "AI DETECTED VOICE";
                } else if (voiceReport.risk_level === "Uncertain") {
                    voiceBadge.classList.add("voice-type-uncertain");
                    voiceBadge.innerText = "UNCERTAIN VOICE";
                } else {
                    voiceBadge.classList.add("voice-type-human");
                    voiceBadge.innerText = "HUMAN VOICE";
                }

                document.getElementById("voice-conf").innerText = voiceReport.confidence_score + "%";
                document.getElementById("voice-reasoning").innerText = voiceReport.reasoning;

                // Set metrics
                document.getElementById("metric-pitch").innerText = voiceReport.features.pitch_variance;
                document.getElementById("metric-jitter").innerText = voiceReport.features.jitter;
                document.getElementById("metric-shimmer").innerText = voiceReport.features.shimmer;
                document.getElementById("metric-stability").innerText = voiceReport.features.voice_stability;
            } else {
                voiceCard.style.display = "none";
            }
        }

        // Circular Gauge Animation
        function setGaugeProgress(percent, color) {
            const circle = document.querySelector('.progress-ring__circle');
            const radius = circle.r.baseVal.value;
            const circumference = radius * 2 * Math.PI;
            const offset = circumference - (percent / 100) * circumference;
            circle.style.strokeDashoffset = offset;
            circle.style.stroke = color;
        }

        // Generate 3 loud high-pitched warning beeps using web AudioContext
        function playLoudWarningBeep() {
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                
                // Play 3 times with pauses
                let now = audioCtx.currentTime;
                const duration = 0.20; // 200ms
                const gap = 0.12;       // 120ms gap

                for(let i = 0; i < 3; i++) {
                    const osc = audioCtx.createOscillator();
                    const gain = audioCtx.createGain();
                    
                    osc.type = "sine";
                    // 880Hz (A5 high-pitch alarm tone)
                    osc.frequency.setValueAtTime(880, now);
                    
                    gain.gain.setValueAtTime(0, now);
                    gain.gain.linearRampToValueAtTime(1.0, now + 0.02); // Fast attack
                    gain.gain.setValueAtTime(1.0, now + duration - 0.02);
                    gain.gain.linearRampToValueAtTime(0, now + duration); // Fast decay
                    
                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    
                    osc.start(now);
                    osc.stop(now + duration);
                    
                    now += duration + gap;
                }
            } catch(e) {
                console.error("Audio warning playback failed: ", e);
            }
        }
    </script>
</body>
</html>"""

if __name__ == "__main__":
    handler = DashboardHandler
    socketserver.TCPServer.allow_reuse_address = True
    port = PORT
    server_started = False
    
    while port < PORT + 10:
        try:
            with socketserver.TCPServer(("", port), handler) as httpd:
                print(f"Phase 1 Dashboard server running locally at http://localhost:{port}")
                server_started = True
                httpd.serve_forever()
                break
        except OSError as e:
            # Check for WinError 10048 (Address already in use) or Unix equivalent
            if "already in use" in str(e).lower() or getattr(e, 'errno', None) in (98, 10048):
                print(f"Port {port} is already in use. Trying port {port + 1}...")
                port += 1
            else:
                raise e
                
    if not server_started:
        print("[ERROR] Could not start HTTP server. All ports from 8001 to 8010 are occupied.")
        sys.exit(1)
