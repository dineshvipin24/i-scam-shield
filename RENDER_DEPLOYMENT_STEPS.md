# 🚀 Deploy AI Voice Detection to Render - STEP BY STEP

## ⏱️ Time Required: 15 minutes

---

## 📋 STEP 1: Train the Model Locally (5 minutes)

### 1a. Install Dependencies
```bash
cd backend/model
pip install -r requirements_ai_voice.txt
```

### 1b. Train Model with Your ElevenLabs Audio
```bash
python quick_train_ai_voice.py --elevenlabs-file "c:\Users\Vipin\Downloads\ElevenLabs_2026-06-07T13_01_52_Roger_pre_sp100_s50_sb75_se0_b_m2.mp3" --train
```

**Wait for it to complete** (should show: "Best model saved")

**Output:** `backend/model/ai_voice_model.pth` (created)

### 1c. Test Locally (Optional but Recommended)
```bash
python quick_train_ai_voice.py --test-file "audio.mp3"
```

✅ Should show predictions like "AI-Generated" with confidence scores

---

## 📋 STEP 2: Add Code to Your FastAPI App (3 minutes)

### 2a. Open `backend/main.py`

Add this at the top (after existing imports):
```python
from backend.model.ai_voice_detector import AIVoiceDetector

# Initialize on startup
ai_voice_detector = AIVoiceDetector()
```

### 2b. Add Endpoint
Copy the voice detection endpoint from `FASTAPI_INTEGRATION.py` and paste it into your `main.py`:

```python
@app.post("/api/detect-voice")
async def detect_voice(file: UploadFile = File(...)):
    """Detect Human vs AI-Generated vs Deepfake voice"""
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

✅ Save the file

---

## 📋 STEP 3: Commit to Git (2 minutes)

### 3a. From Project Root
```bash
# Navigate to your project root
cd c:\Users\Vipin\OneDrive\Desktop\AI\ calling

# Check what changed
git status
```

### 3b. Stage Files
```bash
git add .
```

### 3c. Commit
```bash
git commit -m "Add: AI voice detection to production deployment

- Trained ai_voice_model.pth for human/AI/deepfake detection
- Added FastAPI endpoint for voice analysis
- Updated requirements.txt with torch, scipy, soundfile
- Supports ElevenLabs and other TTS detection"
```

### 3d. Push to GitHub
```bash
git push
```

✅ Wait for upload to complete

---

## 📋 STEP 4: Deploy to Render (5 minutes)

### 4a. Go to Render Dashboard
```
https://dashboard.render.com
```

### 4b. Select Your Service
1. Click on your backend service
2. Should see "Syncing..." then auto-deploy starts
3. Check the **Logs** tab

### 4c. Wait for Deployment
Watch the logs until you see:
```
Successfully deployed
```

⏱️ **This takes 2-5 minutes**

### 4d. Verify Deployment
1. Check Render logs for errors
2. Should see: `Model loaded` or `Demo mode` (if model loading fails)

✅ **Deployment Complete!**

---

## 🧪 STEP 5: Test the API (2 minutes)

### Option A: Using cURL
```bash
curl -X POST https://your-service-name.onrender.com/api/detect-voice \
  -F "file=@audio.mp3"
```

### Option B: Using Python
```python
import requests

url = "https://your-service-name.onrender.com/api/detect-voice"
with open("audio.mp3", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)
    print(response.json())
```

### Option C: Using Postman
1. Method: POST
2. URL: `https://your-service-name.onrender.com/api/detect-voice`
3. Body → form-data → Add file parameter
4. Send

### Expected Response
```json
{
  "prediction": "AI-Generated",
  "confidence": 0.885,
  "probabilities": {
    "human": 0.052,
    "ai_generated": 0.885,
    "deepfake_synthetic": 0.063
  }
}
```

✅ **Working!**

---

## 🆘 TROUBLESHOOTING

### ❌ "Module not found: ai_voice_detector"
**Fix:**
```bash
# Make sure files are in Git
git add backend/model/
git commit -m "Add AI voice detection files"
git push
```

### ❌ "Model file not found"
**Fix:** Make sure `ai_voice_model.pth` was created and pushed
```bash
ls backend/model/ai_voice_model.pth  # Check it exists
git add backend/model/ai_voice_model.pth
git push
```

### ❌ "Timeout during deployment"
**Fix:** Render free plan sometimes slow. Wait 10+ minutes
```bash
# Check logs on Render dashboard for detailed errors
```

### ❌ Response time too slow (>10s)
**Fix:** This is normal for first request (model loads)
- Subsequent requests will be faster
- Use Render's paid instance if needed

### ❌ Out of Memory Error
**Fix:** Use smaller model or CPU-only version:
```bash
# Edit requirements.txt
# Replace: torch==2.3.0
# With: torch-cpu==2.3.0
git push  # Redeploy
```

---

## 📱 STEP 6: Integrate with Android App (5 minutes)

Add to your `CallScreeningServiceImpl.kt`:

```kotlin
private val apiUrl = "https://your-service-name.onrender.com"

suspend fun analyzeVoiceOnBackend(audioBytes: ByteArray) {
    try {
        val client = OkHttpClient()
        val body = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("file", "audio.wav",
                RequestBody.create(MediaType.parse("audio/wav"), audioBytes)
            )
            .build()
        
        val request = Request.Builder()
            .url("$apiUrl/api/detect-voice")
            .post(body)
            .build()
        
        val response = client.newCall(request).execute()
        val json = JSONObject(response.body?.string() ?: "{}")
        
        val prediction = json.optString("prediction")
        val confidence = json.optDouble("confidence")
        
        if (prediction == "AI-Generated" || confidence > 0.7) {
            showScamAlert("⚠️ AI-generated voice detected - possible scam!")
        }
    } catch (e: Exception) {
        Log.e("VoiceDetection", "Error: ${e.message}")
    }
}
```

---

## ✅ FINAL CHECKLIST

Before considering deployment done:

```
□ Model trained locally (ai_voice_model.pth exists)
□ Files committed to Git
□ Code pushed to GitHub
□ Render shows "Successfully deployed"
□ Logs show no errors
□ /api/detect-voice endpoint responds
□ Response includes predictions
□ Android app can call endpoint
```

---

## 🎉 DONE!

Your AI voice detection is now **live on Render**!

### What You Can Do Now:

✅ **Detect AI-Generated Voices** - From ElevenLabs, Google TTS, Polly, etc.
✅ **Detect Human Voices** - Real speech detection
✅ **Detect Deepfakes** - Vocoder-based synthesis detection
✅ **Get Confidence Scores** - Know how certain the model is
✅ **Integrate with Android** - Real-time detection on incoming calls

### Next Steps (Optional):

1. **Improve Accuracy**: Add more training data and retrain
2. **Fine-tune Thresholds**: Adjust confidence levels
3. **Monitor Performance**: Track predictions in Render logs
4. **Scale Up**: Upgrade Render plan if needed

---

## 📞 Support

### Model Questions?
See: `backend/model/README_AI_VOICE.md`

### Render Deployment Issues?
See: `backend/model/RENDER_DEPLOYMENT_GUIDE.md`

### FastAPI Integration?
See: `backend/FASTAPI_INTEGRATION.py`

### Training Questions?
See: `backend/model/AI_VOICE_TRAINING_GUIDE.md`

---

## 🚀 Quick Summary

1. ✅ **Train**: `python quick_train_ai_voice.py --train`
2. ✅ **Code**: Add FastAPI endpoint
3. ✅ **Git**: `git add . && git commit && git push`
4. ✅ **Deploy**: Render auto-deploys
5. ✅ **Test**: POST to `/api/detect-voice`

**That's it! 🎤**
