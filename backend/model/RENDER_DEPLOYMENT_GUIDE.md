# 🚀 Deploying AI Voice Detection to Render

## Overview

You have a FastAPI backend running on Render. Here's how to add the AI voice detection feature.

---

## 📋 Deployment Strategy

### Option A: Quick Deploy (Recommended for Testing)
- Use synthetic model initially (no model file needed)
- Train model locally and add to repo
- Deploy to Render with model file

### Option B: Full Deploy with Trained Model
- Train model locally
- Commit model to Git (if <50MB)
- Or use cloud storage (AWS S3, Google Drive)
- Download on startup if needed

---

## ✅ Step-by-Step Deployment

### Step 1: Update Your Local Files

✅ **Already Done:**
- `requirements.txt` - Updated with torch, scipy, soundfile
- `ai_voice_detector.py` - Created
- `ai_voice_dataset_builder.py` - Created
- All other model files - Created

### Step 2: Train the Model Locally

```bash
cd backend/model
pip install -r requirements_ai_voice.txt

# Train with your ElevenLabs audio
python quick_train_ai_voice.py ^
  --elevenlabs-file "path/to/ElevenLabs_voice.mp3" ^
  --train
```

**Output:** `ai_voice_model.pth` (created in `backend/model/`)

**File size:** ~5-10 MB

### Step 3: Update Git Repository

```bash
# From project root
git add backend/model/
git add backend/requirements.txt

git commit -m "Add: AI voice detection model and training pipeline

- Add AIVoiceClassifier for human/AI/deepfake detection
- Add dataset builder and training scripts  
- Add quick_train and prepare_voice_data utilities
- Add comprehensive documentation and guides
- Train ai_voice_model.pth for ElevenLabs voice detection"

git push
```

### Step 4: Update Your FastAPI App

Add voice detection endpoint to `backend/main.py`:

```python
from backend.model.ai_voice_detector import AIVoiceDetector

# Initialize detector on startup (add this at the top level)
ai_voice_detector = AIVoiceDetector()

@app.post("/api/detect-voice")
async def detect_voice(file: UploadFile = File(...)):
    """
    Detect if voice is Human, AI-Generated, or Deepfake
    """
    try:
        audio_bytes = await file.read()
        prediction, probabilities = ai_voice_detector.predict_pcm(audio_bytes)
        
        return {
            "prediction": prediction,
            "confidence": max(probabilities.values()),
            "probabilities": {
                "human": probabilities["Human"],
                "ai_generated": probabilities["AI-Generated"],
                "deepfake_synthetic": probabilities["Deepfake/Synthetic"]
            }
        }
    except Exception as e:
        return {"error": str(e)}, 400
```

### Step 5: Deploy to Render

```bash
# Push changes (already done in Step 3)
git push

# Go to Render Dashboard
# https://dashboard.render.com

# Your service should auto-deploy from Git

# Monitor deployment
# Logs will show: "Successfully deployed"
```

---

## 🔧 Render Configuration

### If Using Render Web Service:

**Settings to verify:**
- ✅ Build Command: `pip install -r requirements.txt`
- ✅ Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- ✅ Environment: Python 3.11+
- ✅ Instance: Standard (or higher for faster inference)

### If First Time on Render:

**Create new Web Service:**
1. Go to https://dashboard.render.com
2. Click "New" → "Web Service"
3. Connect your GitHub repo
4. Configure:
   - **Name:** your-api-name
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy

---

## 📦 Model File Management

### Small Model (<50MB) - Simple Approach
```bash
# Commit to Git
git add backend/model/ai_voice_model.pth
git commit -m "Add: Trained AI voice detection model"
git push

# Render automatically deploys the file
```

### Large Model or Don't Want in Git - Cloud Storage

**Option 1: AWS S3**
```python
# In main.py startup
import boto3
import os

@app.on_event("startup")
async def download_model_if_needed():
    model_path = "backend/model/ai_voice_model.pth"
    if not os.path.exists(model_path):
        print("Downloading model from S3...")
        s3 = boto3.client('s3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
            aws_secret_access_key=os.getenv('AWS_SECRET_KEY')
        )
        s3.download_file(
            'your-bucket',
            'ai_voice_model.pth',
            model_path
        )
        print("Model downloaded")
```

**Option 2: Google Drive** (Simple for testing)
```python
# Use gdown to download
# pip install gdown
import gdown

@app.on_event("startup")
async def download_model_if_needed():
    model_path = "backend/model/ai_voice_model.pth"
    if not os.path.exists(model_path):
        print("Downloading model...")
        gdown.download(
            id='YOUR_GOOGLE_DRIVE_FILE_ID',
            output=model_path
        )
        print("Model ready")
```

---

## 🧪 Test After Deployment

### Test the Endpoint

```bash
# Replace with your Render URL
curl -X POST https://your-app.onrender.com/api/detect-voice \
  -F "file=@audio.mp3"

# Response should be:
# {
#   "prediction": "AI-Generated",
#   "confidence": 0.885,
#   "probabilities": {
#     "human": 0.052,
#     "ai_generated": 0.885,
#     "deepfake_synthetic": 0.063
#   }
# }
```

### Check Logs on Render

1. Dashboard → Your Service → Logs
2. Should show: `"Model loaded (Accuracy: XX%)"` or demo mode message

---

## 🚨 Common Issues & Solutions

### Issue 1: "Module not found: ai_voice_detector"
**Cause:** Files not in Git or path issues
**Solution:**
```bash
# Ensure files are in backend/model/
ls backend/model/ai_voice_detector.py

# Commit and push
git add backend/model/
git commit -m "Add AI voice detection"
git push
```

### Issue 2: PyTorch Download Too Large (Build Timeout)
**Cause:** Render timeout downloading PyTorch
**Solution:**
```python
# Use CPU-only PyTorch to save space
# In requirements.txt replace:
# torch==2.3.0
# With:
torch-cpu==2.3.0
```

Or use pre-built slim version:
```
torch==2.3.0+cpu
```

### Issue 3: Render Build Fails - "Out of Disk"
**Cause:** Docker build environment too small
**Solution:**
```bash
# Optimize requirements.txt - remove unnecessary packages
# Or upgrade Render instance to "Pro" plan
```

### Issue 4: Model File Too Large
**Cause:** Git rejects files >100MB
**Solution:**
```bash
# Use Git LFS (Large File Storage)
git lfs install
git lfs track "*.pth"
git add backend/model/ai_voice_model.pth
git commit -m "Add large model file via LFS"
git push
```

### Issue 5: Inference Too Slow on Render
**Cause:** Using CPU instead of GPU
**Solution:**
```python
# Render doesn't have free GPU - use:
# 1. Trade-off: Reduce model size
# 2. Or: Use Render's GPU tier (paid)
# 3. Or: Offload to external GPU service

# Quick fix - limit batch size
config = {
    "device": "cpu",
    "batch_size": 8  # Smaller batches
}
```

---

## 📊 Deployment Checklist

Before pushing to production:

```
□ AI voice model trained locally
□ ai_voice_model.pth exists in backend/model/
□ requirements.txt updated with new dependencies
□ Endpoint added to main.py
□ All new files committed to Git
□ Tests pass locally
□ Model loads without errors
□ Endpoint returns correct format
□ Logs show no errors on Render
□ Response time acceptable (<1s)
```

---

## 🔄 Update Workflow Going Forward

### To Update Model with Better Training:

```bash
# 1. Train locally with more data
python backend/model/quick_train_ai_voice.py --train

# 2. Replace old model
cp backend/model/ai_voice_model.pth backend/model/ai_voice_model.pth.bak
# New model is already at ai_voice_model.pth

# 3. Test
python backend/model/quick_train_ai_voice.py --test-file "test.mp3"

# 4. Deploy
git add backend/model/ai_voice_model.pth
git commit -m "Update: Improved AI voice detection model (XX% accuracy)"
git push
```

Render automatically redeploys on push!

---

## 📱 Integrate with Android App

Once deployed, update your Android app:

```kotlin
// In CallScreeningServiceImpl.kt
private val backendUrl = "https://your-app.onrender.com"

suspend fun analyzeVoice(audioBytes: ByteArray) {
    val client = OkHttpClient()
    val body = MultipartBody.Builder()
        .setType(MultipartBody.FORM)
        .addFormDataPart(
            "file",
            "audio.wav",
            RequestBody.create(MediaType.parse("audio/wav"), audioBytes)
        )
        .build()
    
    val request = Request.Builder()
        .url("$backendUrl/api/detect-voice")
        .post(body)
        .build()
    
    val response = client.newCall(request).execute()
    val json = JSONObject(response.body?.string() ?: "{}")
    
    val prediction = json.optString("prediction")
    val confidence = json.optDouble("confidence")
    
    if (prediction == "AI-Generated" || confidence > 0.7) {
        showFraudAlert("AI voice detected")
    }
}
```

---

## 📈 Monitoring

### Setup Monitoring on Render:
1. Dashboard → Your Service → Settings
2. Enable "Metrics"
3. Monitor:
   - CPU usage
   - Memory usage
   - Requests per minute
   - Error rates

### Key Metrics to Watch:
- Response time (target: <500ms per audio)
- Memory spikes during inference
- Error logs for crashes

---

## ✅ Success Criteria

✓ Model deploys without errors  
✓ `/api/detect-voice` endpoint works  
✓ Returns correct predictions  
✓ Response time < 1 second  
✓ Handles various audio formats  
✓ Graceful fallback if model fails  

---

## 🆘 Need Help?

Check logs:
```
# On Render Dashboard → Logs
# Look for errors or warnings
```

Test locally first:
```bash
# Run complete test locally before deploying
python -c "from backend.model.ai_voice_detector import AIVoiceDetector; d = AIVoiceDetector()"
```

---

## 📝 Quick Command Summary

```bash
# Train model
cd backend/model && python quick_train_ai_voice.py --train

# Update Git
git add .
git commit -m "Add AI voice detection to Render deployment"
git push

# Monitor
# Go to https://dashboard.render.com and check logs

# Done! Your Render app auto-deploys
```

That's it! 🚀
