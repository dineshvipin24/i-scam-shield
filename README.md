# 🛡️ AI Scam Call Interceptor

> Real-time cloud-based AI system that intercepts phone calls, detects scams using a PyTorch LSTM model, and automatically warns/disconnects users from fraudulent callers.

## Architecture

```
📱 User's Phone
    ↓ (Conditional Call Forwarding)
☁️ Twilio Voice  →  WebSocket Stream  →  🐍 FastAPI Backend
                                              ├── STT (Deepgram)
                                              ├── PyTorch LSTM Model
                                              └── Twilio REST (Inject Warning / Hangup)
                                                    ↓ REST API
                                         📊 React Native Mobile App
```

## Risk Score Thresholds

| Score    | Status      | Action                         |
|----------|-------------|--------------------------------|
| 0 – 0.40 | ✅ Safe      | Continue call                  |
| 0.41–0.70| ⚠️ Suspicious| Play audio alert               |
| 0.71–1.0 | 🚨 Fraud    | Inject warning + Hangup        |

---

## Quick Start (Demo Mode — No Twilio Needed)

### 1. Setup Backend

```powershell
cd "AI calling\backend"

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env
# (No keys needed for demo mode)

# Train the AI model first
cd model
python train_model.py
cd ..

# Start the server
python main.py
```

Server runs at: `http://localhost:8000`

### 2. Setup Mobile App

```powershell
cd "AI calling\mobile-app"
npm install
npx expo start
```

Scan QR with Expo Go app on your phone.

---

## Full Production Setup

### Step 1: Get Accounts (All Free Tiers Available)

| Service  | Free Tier | Link |
|----------|-----------|------|
| Twilio   | $15 trial credit | https://twilio.com |
| Deepgram | 200 hours free   | https://deepgram.com |
| ngrok    | Free tunnel      | https://ngrok.com |

### Step 2: Configure .env

```env
TWILIO_ACCOUNT_SID=ACxxxxxxxx
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
SERVER_URL=https://abc123.ngrok.io
FORWARD_TO_NUMBER=+91xxxxxxxxxx
STT_PROVIDER=deepgram
DEEPGRAM_API_KEY=your_key
```

### Step 3: Start ngrok

```powershell
ngrok http 8000
# Copy the https://xxx.ngrok.io URL → paste as SERVER_URL in .env
```

### Step 4: Configure Twilio

1. Go to https://console.twilio.com
2. Phone Numbers → Manage → Active Numbers → click your number
3. Voice Configuration → "A call comes in" → Webhook
4. Set URL to: `https://YOUR_NGROK_URL/twiml`
5. Method: `HTTP POST`

### Step 5: Enable Call Forwarding on Your Phone

**Android:**
```
Settings → Call → Supplementary Services → Call Forwarding
→ Forward when unanswered → set to your Twilio number
```

**OR dial:**
```
*61*+1TWILIONUMBER#
```

### Step 6: Train Model

```powershell
cd backend/model
python train_model.py
# Trains for 30 epochs, saves scam_model.pth
# Target: >90% F1 score
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/twiml` | Twilio webhook — returns TwiML |
| WS     | `/stream` | Twilio media stream WebSocket |
| GET    | `/api/calls` | List all call sessions |
| GET    | `/api/calls/{sid}` | Call detail + score timeline |
| GET    | `/api/stats` | Dashboard stats |
| GET    | `/api/settings` | Get settings |
| POST   | `/api/settings` | Update settings |
| GET    | `/api/live/{sid}` | SSE live score stream |
| GET    | `/health` | Health check |

---

## Project Structure

```
AI calling/
├── backend/
│   ├── model/
│   │   ├── train_model.py      ← PyTorch LSTM training
│   │   ├── inference.py        ← Real-time inference engine
│   │   ├── scam_dataset.csv    ← Training data (Hindi + English)
│   │   ├── scam_model.pth      ← Trained weights (after training)
│   │   └── vocab.json          ← Vocabulary (after training)
│   ├── main.py                 ← FastAPI + WebSocket server
│   ├── audio_processor.py      ← mu-law decode + buffering
│   ├── stt_client.py           ← Deepgram / Whisper STT
│   ├── twilio_client.py        ← Twilio REST interventions
│   ├── database.py             ← SQLite ORM
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
└── mobile-app/
    ├── App.js                  ← Navigation + design tokens
    ├── api.js                  ← Backend API service
    ├── screens/
    │   ├── HomeScreen.js       ← Live risk gauge + demo
    │   ├── HistoryScreen.js    ← Call history + detail
    │   └── SettingsScreen.js   ← Controls + setup guide
    └── package.json
```

---

## Tech Stack

| Layer      | Technology                  |
|------------|-----------------------------|
| Telephony  | Twilio Voice API + TwiML    |
| Backend    | Python 3.11 + FastAPI       |
| WebSocket  | uvicorn + starlette         |
| AI Model   | PyTorch + BiLSTM + Attention|
| STT        | Deepgram (Hindi+English)    |
| Database   | SQLite → PostgreSQL (prod)  |
| Mobile App | React Native + Expo         |
| Deployment | Render.com / AWS EC2        |
| Tunneling  | ngrok                       |

---

## Deploy to Render.com (Free)

1. Push code to GitHub
2. Go to https://render.com → New → Web Service
3. Select your repo → `backend/` directory
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables from `.env`

---

## Hackathon Demo Script

1. Show app → tap "▶ Demo Scam Call" on Home screen
2. Watch risk gauge climb from 0% → 95%
3. 🚨 Alert fires at 74% — "FRAUD DETECTED"
4. Explain: "In a real call, the backend would inject an audio warning and hang up"
5. Show Call History → blocked call entry
6. Show Settings → explain sensitivity controls

**Judges will see:** Twilio + WebSocket + PyTorch + FastAPI + React Native — all integrated!
