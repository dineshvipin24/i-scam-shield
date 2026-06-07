package com.campprotect.scamshield.overlay

import android.content.Context
import android.media.AudioAttributes
import android.media.AudioManager
import android.media.MediaPlayer
import android.media.SoundPool
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.speech.tts.TextToSpeech
import android.util.Log
import com.campprotect.scamshield.database.AppDatabase
import com.campprotect.scamshield.database.UserSettings
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.util.Locale

class FraudAlertManager(private val context: Context) : TextToSpeech.OnInitListener {
    private val TAG = "FraudAlertManager"
    private var mediaPlayer: MediaPlayer? = null
    private var soundPool: SoundPool? = null
    private var textToSpeech: TextToSpeech? = null
    private var ttsReady = false
    private var warningBeepId = -1

    // Settings memory cache (fallback to defaults if DB is empty)
    private var activeSettings = UserSettings()

    init {
        loadSettingsAsync()
        initializeSoundPool()
        initializeTTS()
    }

    private fun loadSettingsAsync() {
        CoroutineScope(Dispatchers.IO).launch {
            val db = AppDatabase.getDatabase(context)
            val settings = db.callHistoryDao().getSettings()
            if (settings != null) {
                activeSettings = settings
            } else {
                // Initialize default row
                db.callHistoryDao().saveSettings(activeSettings)
            }
        }
    }

    private fun initializeSoundPool() {
        val audioAttributes = AudioAttributes.Builder()
            .setUsage(AudioAttributes.USAGE_ALARM)
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
            .build()

        soundPool = SoundPool.Builder()
            .setMaxStreams(2)
            .setAudioAttributes(audioAttributes)
            .build()

        try {
            val beepResId = context.resources.getIdentifier("warning_beep", "raw", context.packageName)
            if (beepResId != 0) {
                warningBeepId = soundPool?.load(context, beepResId, 1) ?: -1
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to load warning beep resource: ${e.message}")
        }
    }

    private fun initializeTTS() {
        textToSpeech = TextToSpeech(context, this)
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            val result = textToSpeech?.setLanguage(Locale.getDefault())
            if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                Log.e(TAG, "Language not supported for Text-to-Speech")
            } else {
                ttsReady = true
                Log.d(TAG, "TextToSpeech successfully initialized.")
            }
        } else {
            Log.e(TAG, "TTS Initialization failed.")
        }
    }

    /**
     * Speaks the warning statement.
     */
    fun speakWarningText() {
        if (!activeSettings.enableTTS || !ttsReady) return
        Log.d(TAG, "Speaking voice warning alert")

        val warningMsg = "Warning. Possible scam detected. Do not share OTP, Aadhaar, PAN, CVV, UPI PIN, or banking information."
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            val audioAttributes = AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_VOICE_COMMUNICATION)
                .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                .build()
            
            textToSpeech?.setAudioAttributes(audioAttributes)
            textToSpeech?.speak(warningMsg, TextToSpeech.QUEUE_FLUSH, null, "FraudAlertTTS")
        } else {
            @Suppress("DEPRECATION")
            val params = HashMap<String, String>().apply {
                put(TextToSpeech.Engine.KEY_PARAM_STREAM, AudioManager.STREAM_VOICE_CALL.toString())
            }
            @Suppress("DEPRECATION")
            textToSpeech?.speak(warningMsg, TextToSpeech.QUEUE_FLUSH, params)
        }
    }

    fun playWarningBeep() {
        if (!activeSettings.enableBeep) return
        Log.d(TAG, "Playing Warning Beep (Medium Risk)")

        if (warningBeepId != -1) {
            val vol = activeSettings.alertVolume
            soundPool?.play(warningBeepId, vol, vol, 1, 0, 1.0f)
        } else {
            playFallbackBeep()
        }
    }

    fun playFraudAlarm() {
        if (!activeSettings.enableBeep) return
        Log.d(TAG, "Playing Fraud Alarm (High Risk)")

        stopAlarm()

        try {
            val alarmResId = context.resources.getIdentifier("fraud_alarm", "raw", context.packageName)
            if (alarmResId != 0) {
                mediaPlayer = MediaPlayer.create(context, alarmResId).apply {
                    isLooping = true
                    val vol = activeSettings.alertVolume
                    setVolume(vol, vol)
                    start()
                }
            } else {
                playFallbackAlarm()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to play fraud alarm: ${e.message}")
        }
    }

    fun stopAlarm() {
        mediaPlayer?.let {
            if (it.isPlaying) {
                it.stop()
            }
            it.release()
        }
        mediaPlayer = null
        textToSpeech?.stop()
        Log.d(TAG, "All alarm audio indicators stopped.")
    }

    fun vibrateDevice(pattern: LongArray) {
        if (!activeSettings.enableVibration) return
        Log.d(TAG, "Triggering device vibration")

        val vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
            vibratorManager.defaultVibrator
        } else {
            @Suppress("DEPRECATION")
            context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            vibrator.vibrate(VibrationEffect.createWaveform(pattern, -1))
        } else {
            @Suppress("DEPRECATION")
            vibrator.vibrate(pattern, -1)
        }
    }

    private fun playFallbackBeep() {
        Log.i(TAG, "Beep fallback triggered")
    }

    private fun playFallbackAlarm() {
        Log.i(TAG, "Alarm fallback triggered")
    }

    fun destroy() {
        stopAlarm()
        soundPool?.release()
        soundPool = null
        textToSpeech?.shutdown()
        textToSpeech = null
    }
}
