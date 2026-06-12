# 🚀 Deployment Guide: Railway & Vercel

This guide provides instructions for deploying the **AI Scam Shield** backend to alternative platforms, specifically comparing **Railway** and **Vercel**. 

---

## 📊 Quick Comparison

Before choosing a platform, review how each handles the application's unique architectural requirements:

| Feature | Railway (Recommended) | Vercel (Not Recommended) |
| :--- | :--- | :--- |
| **Hosting Model** | Container-based (PaaS) | Serverless Functions (FaaS) |
| **Execution Limits** | Continuous running | Max 10-15s execution timeout |
| **WebSockets (`/stream`)** | ✅ **Full Support** (Crucial for Twilio/WebRTC) | ❌ **No Support** (WebSockets will fail) |
| **System Libraries** | ✅ **Full Support** (Via Dockerfile: `libavformat`, `gcc`, etc.) | ❌ **No Support** (Cannot install packages via `apt-get`) |
| **Persistent SQLite** | ✅ **Supported** (Via persistent volume mount) | ❌ **No Support** (Ephemeral read-only filesystem) |
| **Ease of Deployment** | Automatic build from GitHub | Automatic build from GitHub |

> [!IMPORTANT]
> **Why Vercel will fail:**
> 1. **WebRTC/Audio Processing:** The backend relies on `aiortc` and `av` (PyAV) for real-time audio resampling. These packages require C-libraries (`libavformat-dev`, `libavcodec-dev`, etc.) to be installed on the host OS. On Vercel, you cannot run `apt-get` to install these libraries, causing the build to fail.
> 2. **No WebSockets:** Twilio streams call audio in real-time over a WebSocket connection (`/stream`). Vercel Serverless functions terminate after returning a response and do not support open socket connections.

---

## 🚂 Option 1: Deploying to Railway (Recommended)

Railway runs our existing containerized configuration (using `backend/Dockerfile` and the newly created `railway.json` at the root).

### Step 1: Push Configurations to GitHub
Make sure the new configuration files are committed and pushed to your GitHub repository:
```bash
git add railway.json vercel.json
git commit -m "Add Railway and Vercel configuration files"
git push origin main
```
*(You can also use your `push_to_github.bat` script to push the changes).*

### Step 2: Create a Railway Project
1. Go to [Railway.app](https://railway.app) and sign in with your GitHub account.
2. Click **New Project** in the upper right.
3. Select **Deploy from GitHub repo**.
4. Choose your repository: `dineshvipin24/i-scam-shield`.

### Step 3: Configure the Service
Once you select the repository, Railway will detect the configuration:
1. Railway reads the `railway.json` file at the root.
2. It automatically sets the build context to the `/backend` directory and compiles the container using `/backend/Dockerfile`.
3. Under the service's **Settings** tab:
   - Ensure the **Root Directory** is empty or set to `/` (Railway reads the context from `railway.json`).
   - If you prefer not to use `railway.json`, you can delete it and manually set the **Root Directory** to `/backend` in the Railway dashboard, and Railway will find the `Dockerfile` inside it.

### Step 4: Set Environment Variables
Go to the **Variables** tab of your service in Railway and add the following variables:

| Variable Name | Value | Purpose |
| :--- | :--- | :--- |
| `PORT` | `8000` (or leave default) | The port FastAPI will run on |
| `FORWARD_TO_NUMBER` | `+91XXXXXXXXXX` | The phone number to forward known or safe calls to |
| `TWILIO_ACCOUNT_SID` | *Your Twilio SID* | Required if using Twilio call control features |
| `TWILIO_AUTH_TOKEN` | *Your Twilio Auth Token* | Required if using Twilio call control features |
| `EXPO_ACCESS_TOKEN` | *Your Expo Token* | Required for pushing notifications to the mobile app |

### Step 5: (Optional) Set up Persistent SQLite
If you want to keep call logs and contact lists between redeployments:
1. In the Railway project board, click **New** -> **Volume**.
2. Mount the volume to the path `/app/scam_shield.db` or change your database path in `.env` to point to a mounted folder like `/data/scam_shield.db`.
3. *Note: If you do not mount a volume, the SQLite database will reset to its initial state every time you redeploy or the container restarts.*

---

## ⚡ Option 2: Deploying to Vercel (Only for stateless REST APIs)

If you *only* want to host the HTTP JSON endpoints (like `/api/analyze-text` or `/api/detect-voice`) and **do not** require WebSockets or real-time call monitoring, you can deploy a stripped-down version to Vercel.

### Steps to Deploy:
1. Install the Vercel CLI: `npm install -g vercel`
2. Run `vercel` in the project root.
3. Link it to your Vercel account and project.
4. *Caution: As noted above, you must remove `aiortc` and `av` from `requirements.txt` to get the build to succeed, and you will not be able to use the `/stream` endpoints.*

---

## 🧪 Testing the Deployment

Once Railway is deployed, you will be given a public URL (e.g., `https://i-scam-shield-production.up.railway.app`).

### Test 1: Health Check
Open your browser and navigate to:
```
https://your-railway-url.up.railway.app/health
```
You should see:
```json
{
  "status": "ok",
  "model_loaded": true,
  "time": "2026-06-12..."
}
```

### Test 2: Voice Detection Endpoint
Submit a test audio file to the PyTorch AI voice detection endpoint:
```bash
curl -X POST https://your-railway-url.up.railway.app/api/detect-voice \
  -F "file=@path/to/test_voice.mp3"
```
Response format:
```json
{
  "prediction": "Human",
  "confidence": 0.942,
  "probabilities": {
    "human": 0.942,
    "ai_generated": 0.045,
    "deepfake_synthetic": 0.013
  },
  "message": "Voice analysis complete"
}
```
