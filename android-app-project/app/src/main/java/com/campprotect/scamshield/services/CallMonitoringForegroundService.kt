package com.campprotect.scamshield.services

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import com.campprotect.scamshield.database.AppDatabase
import com.campprotect.scamshield.database.CallHistory
import com.campprotect.scamshield.database.FraudAlertLog
import com.campprotect.scamshield.overlay.AlertOverlayService
import com.campprotect.scamshield.overlay.FraudAlertManager
import com.campprotect.scamshield.scamdetection.ScamDetectionEngine
import com.campprotect.scamshield.speech.SpeechRecognizerManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class CallMonitoringForegroundService : Service() {

    private val TAG = "MonitoringService"
    private val CHANNEL_ID = "CallMonitorChannel"
    
    private var speechManager: SpeechRecognizerManager? = null
    private var alertManager: FraudAlertManager? = null
    private val scamEngine = ScamDetectionEngine()

    private var currentCallNumber = ""
    private var rollingTranscript = StringBuilder()
    private var maxScoreReached = 0
    private var detectedCategory = "Safe Call"
    private val triggeredKeywords = mutableSetOf<String>()

    private var alertTriggeredMedium = false
    private var alertTriggeredHigh = false

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onCreate() {
        super.onCreate()
        alertManager = FraudAlertManager(applicationContext)
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        currentCallNumber = intent?.getStringExtra("EXTRA_PHONE_NUMBER") ?: "Unknown Number"
        
        // Comply with Android 14+ Foreground Service types
        val notification = createNotification()
        startForeground(2001, notification)

        // Reset tracking variables
        rollingTranscript.clear()
        maxScoreReached = 0
        detectedCategory = "Safe Call"
        triggeredKeywords.clear()
        alertTriggeredMedium = false
        alertTriggeredHigh = false

        // Broadcast active monitoring status to update UI
        sendMonitoringBroadcast(true)

        // Initialize and trigger STT
        speechManager = SpeechRecognizerManager(this) { text, isFinal ->
            if (isFinal) {
                rollingTranscript.append(" ").append(text)
            }
            val currentSegment = if (isFinal) rollingTranscript.toString() else "${rollingTranscript} $text"
            analyzeSpeech(currentSegment, text)
        }
        speechManager?.startListening()

        Log.d(TAG, "Foreground microphone recording service started for: $currentCallNumber")
        return START_NOT_STICKY
    }

    private fun analyzeSpeech(fullText: String, latestPhrase: String) {
        val result = scamEngine.evaluateTranscript(fullText)
        if (result.confidenceScore > maxScoreReached) {
            maxScoreReached = result.confidenceScore
        }
        detectedCategory = result.category
        triggeredKeywords.addAll(result.matchedKeywords)

        // Broadcast stats to MainActivity UI
        val updateIntent = Intent("com.campprotect.scamshield.SCAM_UPDATE").apply {
            putExtra("SCORE", maxScoreReached)
            putExtra("PHRASE", latestPhrase)
            putExtra("CATEGORY", detectedCategory)
        }
        sendBroadcast(updateIntent)

        // 100% scam threat check: automatically hang up call
        if (maxScoreReached >= 100) {
            Log.d(TAG, "Scam threat score reached 100%! Initiating automatic call termination.")
            alertManager?.stopAlarm()
            alertManager?.vibrateDevice(longArrayOf(0, 800, 100, 800))
            
            // Speak call termination alert
            alertManager?.speakWarningText()

            // Update UI/Overlay with call terminated warning
            showOverlayWarning(100, result.matchedKeywords, "Terminated (100% Scam Threat)")
            logAlertToDatabase(100, result.matchedKeywords, "Call automatically hung up due to 100% scam score.", "FRAUD")
            
            // Auto terminate background recording service (simulates call hang up)
            stopSelf()
            return
        }

        // Active beeping alerts for >= 70%
        if (maxScoreReached >= 70) {
            if (!alertTriggeredHigh) {
                alertTriggeredHigh = true
                alertManager?.playFraudAlarm()
                alertManager?.vibrateDevice(longArrayOf(0, 500, 200, 500, 200, 500))
                alertManager?.speakWarningText()

                showOverlayWarning(maxScoreReached, result.matchedKeywords, result.category)
                logAlertToDatabase(maxScoreReached, result.matchedKeywords, latestPhrase, "HIGH")
            }
        } else if (result.riskLevel == ScamDetectionEngine.RiskLevel.MEDIUM) {
            if (!alertTriggeredMedium) {
                alertTriggeredMedium = true
                alertManager?.playWarningBeep()
                alertManager?.vibrateDevice(longArrayOf(0, 300))
                
                showOverlayWarning(maxScoreReached, result.matchedKeywords, result.category)
                logAlertToDatabase(maxScoreReached, result.matchedKeywords, latestPhrase, "MEDIUM")
            }
        }
    }

    private fun showOverlayWarning(score: Int, keywords: List<String>, category: String) {
        val intent = Intent(this, AlertOverlayService::class.java).apply {
            putExtra("EXTRA_PHONE_NUMBER", currentCallNumber)
            putExtra("EXTRA_RISK_SCORE", score)
            putStringArrayListExtra("EXTRA_KEYWORDS", ArrayList(keywords))
            putExtra("EXTRA_CATEGORY", category)
        }
        startService(intent)
    }

    private fun logAlertToDatabase(score: Int, keywords: List<String>, phrase: String, level: String) {
        val firstKeyword = keywords.firstOrNull() ?: "pattern match"
        CoroutineScope(Dispatchers.IO).launch {
            val db = AppDatabase.getDatabase(applicationContext)
            db.callHistoryDao().insertAlertLog(
                FraudAlertLog(
                    phoneNumber = currentCallNumber,
                    timestamp = System.currentTimeMillis(),
                    riskScore = score,
                    triggerKeyword = firstKeyword,
                    alertType = level,
                    transcriptSnippet = phrase,
                    category = detectedCategory
                )
            )
        }
    }

    private fun sendMonitoringBroadcast(active: Boolean) {
        val intent = Intent("com.campprotect.scamshield.MONITOR_STATUS").apply {
            putExtra("ACTIVE", active)
            putExtra("PHONE", currentCallNumber)
        }
        sendBroadcast(intent)
    }

    override fun onDestroy() {
        super.onDestroy()
        speechManager?.stopListening()
        speechManager?.destroy()
        speechManager = null

        alertManager?.stopAlarm()
        alertManager?.destroy()
        alertManager = null

        // Stop Overlay banner
        stopService(Intent(this, AlertOverlayService::class.java))

        // Save Call Record to DB
        saveCallHistory()

        sendMonitoringBroadcast(false)
        Log.d(TAG, "Foreground microphone monitoring service stopped.")
    }

    private fun saveCallHistory() {
        val finalTranscript = rollingTranscript.toString().trim()
        val finalRiskLevel = when {
            maxScoreReached >= 61 -> "HIGH"
            maxScoreReached >= 31 -> "MEDIUM"
            else -> "LOW"
        }

        CoroutineScope(Dispatchers.IO).launch {
            val db = AppDatabase.getDatabase(applicationContext)
            val settings = db.callHistoryDao().getSettings()
            
            // Only save if history tracking is enabled in UserSettings
            if (settings == null || settings.saveCallHistory) {
                db.callHistoryDao().insertCall(
                    CallHistory(
                        phoneNumber = currentCallNumber,
                        timestamp = System.currentTimeMillis(),
                        transcript = finalTranscript.ifEmpty { "No conversation captured" },
                        riskScore = maxScoreReached,
                        riskLevel = finalRiskLevel,
                        classification = detectedCategory
                    )
                )
            }
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Active Call Screening Service",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Camp Protect Monitor Active")
            .setContentText("Local microphone analyzing call for scam indicators...")
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setOngoing(true)
            .build()
    }
}
