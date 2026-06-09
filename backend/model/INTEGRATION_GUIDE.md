"""
Integration Guide: Adding AI Voice Detection to Your Scam Detection System

This shows how to integrate the new AI voice detector with your existing system.
"""

# ==============================================================================
# 1. BACKEND INTEGRATION (Python)
# ==============================================================================

# In backend/main.py or your Flask app:

from backend.model.ai_voice_detector import AIVoiceDetector
from backend.model.deepfake_classifier import DeepfakeInference

# Initialize detectors (do this once on app startup)
deepfake_detector = DeepfakeInference()
ai_voice_detector = AIVoiceDetector()

@app.route('/analyze-audio', methods=['POST'])
def analyze_audio():
    """
    Analyze audio from a call using both detectors.
    """
    audio_bytes = request.files['audio'].read()
    
    # Run both classifiers
    deepfake_score = deepfake_detector.predict_pcm(audio_bytes)
    voice_type, voice_probs = ai_voice_detector.predict_pcm(audio_bytes)
    
    # Combined analysis
    is_suspicious = False
    reasons = []
    
    if deepfake_score > 0.7:
        is_suspicious = True
        reasons.append(f"Deepfake detected (score: {deepfake_score:.1%})")
    
    if voice_probs['AI-Generated'] > 0.6:
        is_suspicious = True
        reasons.append(f"AI-Generated voice detected ({voice_probs['AI-Generated']:.1%})")
    
    if voice_probs['Deepfake/Synthetic'] > 0.6:
        is_suspicious = True
        reasons.append(f"Synthetic voice detected ({voice_probs['Deepfake/Synthetic']:.1%})")
    
    return {
        'is_suspicious': is_suspicious,
        'voice_type': voice_type,
        'deepfake_score': float(deepfake_score),
        'voice_probabilities': {k: float(v) for k, v in voice_probs.items()},
        'reasons': reasons,
        'confidence': max(
            deepfake_score,
            max(voice_probs.values())
        )
    }


# ==============================================================================
# 2. ANDROID INTEGRATION (Kotlin)
# ==============================================================================

# In CallScreeningServiceImpl.kt
// Example of how to call the Python backend

class CallScreeningServiceImpl : CallScreeningService() {
    
    override fun onScreenCall(request: Call.Details): Call.Response {
        val callId = request.handle.schemeSpecificPart
        
        // Capture audio from the call
        val audioBytes = captureCallAudio()
        
        // Send to backend for analysis
        val analysis = analyzeAudioWithBackend(audioBytes)
        
        // Check results
        if (analysis["is_suspicious"] == true) {
            val reasons = analysis["reasons"] as? List<String> ?: emptyList()
            val voiceType = analysis["voice_type"] as? String ?: "Unknown"
            
            // Alert user
            showFraudAlert(
                title = "Potential Scam Detected",
                message = "Analysis: $voiceType\nReasons: ${reasons.joinToString(", ")}",
                callId = callId
            )
            
            // Block or screen the call
            return if (shouldBlock(voiceType)) {
                Call.Response().setDisconnectAndAddToCallLog(true)
            } else {
                Call.Response().setScreenedCallNotification(true)
            }
        }
        
        return Call.Response()
    }
    
    private fun analyzeAudioWithBackend(audioBytes: ByteArray): Map<String, Any> {
        // Call the Python backend
        val client = OkHttpClient()
        val body = RequestBody.create(
            MediaType.parse("audio/wav"),
            audioBytes
        )
        
        val request = Request.Builder()
            .url("${BACKEND_URL}/analyze-audio")
            .post(body)
            .build()
        
        val response = client.newCall(request).execute()
        val json = JSONObject(response.body?.string() ?: "{}")
        
        return mapOf(
            "is_suspicious" to json.optBoolean("is_suspicious"),
            "voice_type" to json.optString("voice_type"),
            "reasons" to json.optJSONArray("reasons")?.let {
                (0 until it.length()).map { i -> it.getString(i) }
            } ?: emptyList(),
            "confidence" to json.optDouble("confidence")
        )
    }
}


# ==============================================================================
# 3. TRAINING WORKFLOW
# ==============================================================================

"""
Step 1: Prepare Training Data
"""

# Copy your ElevenLabs audio to the right location
# voice_data/elevenlabs/ElevenLabs_2026-06-07T13_01_52_Roger.mp3

# Add human voice samples
# voice_data/human_voices/sample1.wav
# voice_data/human_voices/sample2.mp3
# voice_data/human_voices/podcasts/*

# Add any deepfake samples
# voice_data/deepfake_synthetic/*


"""
Step 2: Train the Model
"""

# cd backend/model
# python quick_train_ai_voice.py --train

# Or with more control:
# python quick_train_ai_voice.py \
#   --elevenlabs-file path/to/file.mp3 \
#   --human-samples 200 \
#   --train


"""
Step 3: Evaluate Results
"""

# python quick_train_ai_voice.py --test-file test_audio.mp3


"""
Step 4: Deploy
"""

# The model is automatically saved to: ai_voice_model.pth
# It will be loaded automatically when AIVoiceDetector() is initialized


# ==============================================================================
# 4. ADVANCED: CUSTOM TRAINING WITH YOUR DATA
# ==============================================================================

from backend.model.ai_voice_dataset_builder import AIVoiceDatasetBuilder
from backend.model.train_ai_voice_model import AIVoiceTrainer
import torch

# Create dataset builder
builder = AIVoiceDatasetBuilder()

# Add files programmatically
builder.add_audio_file(
    "voice_data/elevenlabs/sample.mp3",
    label="ai-generated",
    source="ElevenLabs"
)

builder.add_directory(
    "voice_data/human_voices/",
    label="human",
    source="user_recorded"
)

# Check dataset stats
stats = builder.get_dataset_stats()
print(f"Dataset: {stats['total_samples']} samples")
print(f"Distribution: {stats['distribution']}")

# Configure and train
config = {
    "epochs": 50,
    "batch_size": 32,
    "learning_rate": 0.0005,
    "device": "cuda" if torch.cuda.is_available() else "cpu"
}

trainer = AIVoiceTrainer(config)
train_loader, val_loader = trainer.prepare_dataset("voice_dataset")
best_acc = trainer.train(train_loader, val_loader, "ai_voice_model.pth")

print(f"Training complete. Best accuracy: {best_acc:.2%}")


# ==============================================================================
# 5. UPDATING THE SCAM DETECTION ENGINE
# ==============================================================================

"""
Update ScamDetectionEngine.kt to use voice detection
"""

// In backend/android-app/scamdetection/ScamDetectionEngine.kt

class ScamDetectionEngine(private val callHistoryDao: CallHistoryDao) {
    
    private val voiceDetector by lazy { AIVoiceDetectorWrapper() }
    
    suspend fun analyzeCallSuspect(
        callerId: String,
        audioBytes: ByteArray
    ): ScamDetectionResult {
        
        val callerReputation = getCallerReputation(callerId)
        
        // Voice analysis
        val voiceAnalysis = voiceDetector.analyzeVoice(audioBytes)
        
        var suspicionScore = 0.0
        val factors = mutableListOf<String>()
        
        // Factor 1: Voice characteristics
        when (voiceAnalysis.voiceType) {
            "AI-Generated" -> {
                suspicionScore += 0.4
                factors.add("AI-Generated voice detected")
            }
            "Deepfake/Synthetic" -> {
                suspicionScore += 0.5
                factors.add("Deepfake/Synthetic voice detected")
            }
            else -> {
                // Human voice - lower suspicion
                if (voiceAnalysis.aiGeneratedConfidence > 0.7) {
                    suspicionScore += 0.3
                    factors.add("Possible AI-generated voice")
                }
            }
        }
        
        // Factor 2: Combine with existing reputation data
        if (callerReputation.isBlacklisted) {
            suspicionScore += 0.3
            factors.add("Caller on blacklist")
        }
        
        if (callerReputation.reportCount > 5) {
            suspicionScore += 0.2
            factors.add("Multiple fraud reports")
        }
        
        // Factor 3: Combine with number spoofing detection
        // ... (existing spoofing detection code)
        
        return ScamDetectionResult(
            isSuspicious = suspicionScore > 0.5,
            suspicionScore = suspicionScore,
            factors = factors,
            voiceType = voiceAnalysis.voiceType,
            voiceConfidence = voiceAnalysis.confidence
        )
    }
}


# ==============================================================================
# 6. MONITORING AND FEEDBACK LOOP
# ==============================================================================

"""
Track model performance in production
"""

class ModelPerformanceTracker {
    
    fun logPrediction(
        audio_id: str,
        actual_label: str,  # What it actually was (human, ai, deepfake)
        predicted_label: str,  # What model predicted
        confidence: float,
        timestamp: datetime
    ):
        """Log predictions for later analysis"""
        
        self.db.insert("model_predictions", {
            "audio_id": audio_id,
            "actual": actual_label,
            "predicted": predicted_label,
            "confidence": confidence,
            "correct": actual_label == predicted_label,
            "timestamp": timestamp
        })
    
    def get_accuracy(self, time_window_days: int = 7) -> dict:
        """Calculate model accuracy over time"""
        
        results = self.db.query("""
            SELECT 
                predicted,
                COUNT(*) as total,
                SUM(CASE WHEN correct THEN 1 ELSE 0 END) as correct
            FROM model_predictions
            WHERE timestamp > NOW() - INTERVAL '{time_window_days} days'
            GROUP BY predicted
        """)
        
        return {
            r["predicted"]: r["correct"] / r["total"]
            for r in results
        }
    
    def get_misclassified(self, limit: int = 100) -> list:
        """Get samples the model got wrong (for retraining)"""
        
        return self.db.query("""
            SELECT * FROM model_predictions
            WHERE correct = FALSE
            LIMIT {limit}
        """)


# ==============================================================================
# 7. DEPLOYMENT CHECKLIST
# ==============================================================================

"""
Before deploying to production:

□ Train model with diverse data (200+ samples per class)
□ Validate accuracy on test set (target: >85%)
□ Test with real call audio samples
□ Test with various audio qualities and background noise
□ Benchmark inference time (<500ms per audio)
□ Verify GPU/CPU performance as needed
□ Document expected accuracy and limitations
□ Set up model versioning and rollback capability
□ Create monitoring for model performance
□ Set up retraining pipeline for periodic updates
□ Test integration with Android app
□ Load test with multiple concurrent requests
□ Plan for model updates (versioning strategy)
□ Document fallback behavior if model fails
□ Create documentation for operations team
"""

# ==============================================================================
# 8. FUTURE ENHANCEMENTS
# ==============================================================================

"""
Planned improvements:

1. Real-time streaming inference
   - Process audio chunks as they arrive
   - Provide alerts before call completes

2. Multi-language support
   - Train on various languages
   - Language-specific models

3. Background noise robustness
   - Train on noisy call audio
   - Robustness evaluation

4. Custom TTS detection
   - Identify specific TTS systems
   - Track emerging voice generation services

5. Fine-grained classification
   - Not just "AI-Generated" but which TTS?
   - Confidence levels and uncertainty estimation

6. Adaptive models
   - Online learning from feedback
   - Continual model improvement

7. Ensemble methods
   - Combine multiple models
   - Voting and stacking

8. Explainability
   - Show which audio features triggered detection
   - Visualize decision boundaries
"""

# ==============================================================================
