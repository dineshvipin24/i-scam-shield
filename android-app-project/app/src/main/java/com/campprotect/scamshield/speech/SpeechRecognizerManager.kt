package com.campprotect.scamshield.speech

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.util.Log

class SpeechRecognizerManager(
    private val context: Context,
    private val onResultCallback: (text: String, isFinal: Boolean) -> Unit
) {
    private val TAG = "SpeechRecognizerManager"
    private var speechRecognizer: SpeechRecognizer? = null
    private var recognizerIntent: Intent? = null
    private var isListening = false

    init {
        initializeRecognizer()
    }

    private fun initializeRecognizer() {
        if (SpeechRecognizer.isRecognitionAvailable(context)) {
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context)
            recognizerIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 5)
                // Force offline model usage for privacy compliance if supported
                putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
            }

            speechRecognizer?.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {
                    Log.d(TAG, "On-device Speech Recognizer ready for input.")
                }

                override fun onBeginningOfSpeech() {}

                override fun onRmsChanged(rmsdB: Float) {}

                override fun onBufferReceived(buffer: ByteArray?) {}

                override fun onEndOfSpeech() {}

                override fun onError(error: Int) {
                    val message = getErrorText(error)
                    Log.d(TAG, "Speech recognition error occurred: $message")
                    
                    // Auto restart on timeouts or connection glitches to maintain continuous monitoring
                    if (isListening) {
                        restartListening()
                    }
                }

                override fun onResults(results: Bundle?) {
                    val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    if (!matches.isNullOrEmpty()) {
                        val finalResult = matches[0]
                        Log.d(TAG, "Final Transcription snippet: $finalResult")
                        onResultCallback(finalResult, true)
                    }
                    if (isListening) {
                        restartListening()
                    }
                }

                override fun onPartialResults(partialResults: Bundle?) {
                    val matches = partialResults?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    if (!matches.isNullOrEmpty()) {
                        val partialResult = matches[0]
                        Log.d(TAG, "Partial transcription snippet: $partialResult")
                        onResultCallback(partialResult, false)
                    }
                }

                override fun onEvent(eventType: Int, params: Bundle?) {}
            })
        } else {
            Log.e(TAG, "Speech recognition not available on this device configuration.")
        }
    }

    fun startListening() {
        if (speechRecognizer == null) initializeRecognizer()
        isListening = true
        speechRecognizer?.startListening(recognizerIntent)
    }

    fun stopListening() {
        isListening = false
        speechRecognizer?.stopListening()
    }

    private fun restartListening() {
        if (!isListening) return
        speechRecognizer?.cancel()
        speechRecognizer?.startListening(recognizerIntent)
    }

    fun destroy() {
        isListening = false
        speechRecognizer?.cancel()
        speechRecognizer?.destroy()
        speechRecognizer = null
    }

    private fun getErrorText(errorCode: Int): String {
        return when (errorCode) {
            SpeechRecognizer.ERROR_AUDIO -> "Audio recording error"
            SpeechRecognizer.ERROR_CLIENT -> "Client-side error"
            SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Insufficient permissions"
            SpeechRecognizer.ERROR_NETWORK -> "Network error"
            SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "Network timeout"
            SpeechRecognizer.ERROR_NO_MATCH -> "No speech match found"
            SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "Recognizer service busy"
            SpeechRecognizer.ERROR_SERVER -> "Server-side error"
            SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "No speech input timeout"
            else -> "Unknown SpeechRecognizer error ($errorCode)"
        }
    }
}
