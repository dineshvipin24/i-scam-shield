# phase1-prototype/dashboard.py
import http.server
import socketserver
import json
import os
import urllib.parse
from dataset_builder import DATASET_FILE
from fraud_detector import FraudDetector

PORT = 8001
detector = FraudDetector()

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
            self.wfile.write(json.dumps(self.get_dataset_stats()).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/analyze":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                text = data.get("text", "")
                result = detector.evaluate_text(text)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def get_dataset_stats(self) -> dict:
        total = 0
        scams = 0
        safes = 0
        if os.path.exists(DATASET_FILE):
            import csv
            with open(DATASET_FILE, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                next(reader)
                for row in reader:
                    total += 1
                    if len(row) >= 3 and row[2] == '1':
                        scams += 1
                    else:
                        safes += 1
        return {"total": total, "scams": scams, "safes": safes}

    def get_html_content(self) -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Camp Protect — Phase 1 AI Prototype Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Outfit', sans-serif;
        }
        body {
            background-color: #0A0F1D;
            color: #E2E8F0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }
        .container {
            max-width: 900px;
            width: 100%;
        }
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        header h1 {
            font-size: 32px;
            font-weight: 800;
            color: #64B5F6;
            margin-bottom: 10px;
            letter-spacing: 0.5px;
        }
        header p {
            color: #94A3B8;
            font-size: 15px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 45px;
        }
        .stat-card {
            background: rgba(30, 41, 59, 0.4);
            border: 1px solid #1E293B;
            padding: 20px;
            border-radius: 16px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        .stat-card h3 {
            font-size: 13px;
            color: #94A3B8;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        .stat-card p {
            font-size: 28px;
            font-weight: 800;
            color: #FFF;
        }
        .main-card {
            background: #111827;
            border: 1px solid #1F2937;
            border-radius: 24px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            margin-bottom: 40px;
        }
        textarea {
            width: 100%;
            height: 120px;
            background-color: #0F172A;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 16px;
            color: #FFF;
            font-size: 14.5px;
            resize: none;
            outline: none;
            margin-bottom: 20px;
            transition: border-color 0.2s;
        }
        textarea:focus {
            border-color: #64B5F6;
        }
        button {
            width: 100%;
            background-color: #64B5F6;
            color: #0A0F1D;
            border: none;
            border-radius: 12px;
            padding: 14px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        button:hover {
            opacity: 0.9;
        }
        .result-section {
            margin-top: 30px;
            padding-top: 30px;
            border-top: 1px solid #1F2937;
            display: none;
        }
        .result-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .score-gauge {
            font-size: 40px;
            font-weight: 800;
        }
        .level-badge {
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 12px;
            letter-spacing: 0.5px;
        }
        .level-high { background-color: #EF4444; color: #FFF; }
        .level-medium { background-color: #F59E0B; color: #000; }
        .level-low { background-color: #10B981; color: #FFF; }
        
        .result-details {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 20px;
        }
        .detail-item {
            background-color: #0F172A;
            padding: 16px;
            border-radius: 12px;
            border: 1px solid #1E293B;
        }
        .detail-item h4 {
            font-size: 12px;
            color: #94A3B8;
            margin-bottom: 6px;
            text-transform: uppercase;
        }
        .detail-item p {
            font-weight: 600;
            color: #FFF;
        }
        .evidence-box {
            background-color: #0F172A;
            padding: 16px;
            border-radius: 12px;
            border: 1px dashed #334155;
            color: #CBD5E1;
            font-size: 14px;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>CAMP PROTECT</h1>
            <p>Phase 1 Artificial Intelligence Scam Classifier Engine</p>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Dataset Corpos</h3>
                <p id="stat-total">--</p>
            </div>
            <div class="stat-card">
                <h3>Scam Samples</h3>
                <p id="stat-scam" style="color: #EF4444">--</p>
            </div>
            <div class="stat-card">
                <h3>Safe Samples</h3>
                <p id="stat-safe" style="color: #10B981">--</p>
            </div>
        </div>

        <div class="main-card">
            <textarea id="transcript-input" placeholder="Type or paste a call transcript here to test the AI evaluation model..."></textarea>
            <button onclick="analyzeTranscript()">Run Threat Evaluation</button>

            <div class="result-section" id="results">
                <div class="result-header">
                    <div>
                        <p style="font-size: 13px; color: #94A3B8; text-transform: uppercase; margin-bottom: 4px;">Scam Risk Probability</p>
                        <div class="score-gauge" id="res-score">0%</div>
                    </div>
                    <span class="level-badge" id="res-badge">LOW</span>
                </div>

                <div class="result-details">
                    <div class="detail-item">
                        <h4>Scam Category</h4>
                        <p id="res-cat">--</p>
                    </div>
                    <div class="detail-item">
                        <h4>Confidence Score</h4>
                        <p id="res-conf">0.0</p>
                    </div>
                    <div class="detail-item">
                        <h4>Keywords Flagged</h4>
                        <p id="res-keywords" style="color: #F59E0B">--</p>
                    </div>
                    <div class="detail-item">
                        <h4>Phrase Patterns</h4>
                        <p id="res-patterns" style="color: #F59E0B">--</p>
                    </div>
                </div>

                <div class="evidence-box">
                    <strong>Evidence Analysis Report:</strong>
                    <p id="res-evidence" style="margin-top: 8px; font-style: italic;"></p>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Load dataset counts on init
        fetch('/api/stats')
            .then(res => res.json())
            .then(data => {
                document.getElementById("stat-total").innerText = data.total;
                document.getElementById("stat-scam").innerText = data.scams;
                document.getElementById("stat-safe").innerText = data.safes;
            });

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
                document.getElementById("results").style.display = "block";
                document.getElementById("res-score").innerText = data.risk_score + "%";
                document.getElementById("res-cat").innerText = data.fraud_category;
                document.getElementById("res-conf").innerText = data.confidence_score;
                document.getElementById("res-keywords").innerText = data.detected_keywords.join(", ") || "None";
                document.getElementById("res-patterns").innerText = data.detected_patterns.join(", ") || "None";
                document.getElementById("res-evidence").innerText = data.evidence_report;
                
                // Color gauges
                const badge = document.getElementById("res-badge");
                const scoreText = document.getElementById("res-score");
                badge.className = "level-badge";
                
                if(data.risk_level === "HIGH") {
                    badge.classList.add("level-high");
                    badge.innerText = "HIGH RISK";
                    scoreText.style.color = "#EF4444";
                } else if(data.risk_level === "MEDIUM") {
                    badge.classList.add("level-medium");
                    badge.innerText = "MEDIUM RISK";
                    scoreText.style.color = "#F59E0B";
                } else {
                    badge.classList.add("level-low");
                    badge.innerText = "SAFE";
                    scoreText.style.color = "#10B981";
                }
            });
        }
    </script>
</body>
</html>"""

if __name__ == "__main__":
    handler = DashboardHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Phase 1 Dashboard server running locally at http://localhost:{PORT}")
        httpd.serve_forever()
