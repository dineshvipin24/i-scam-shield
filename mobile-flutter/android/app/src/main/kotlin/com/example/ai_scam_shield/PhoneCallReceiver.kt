package com.example.ai_scam_shield

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.telephony.TelephonyManager
import android.util.Log

class PhoneCallReceiver : BroadcastReceiver() {
    companion object {
        private var lastState: String? = null
        private var lastIncomingNumber: String? = null
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != TelephonyManager.ACTION_PHONE_STATE_CHANGED) return

        val state = intent.getStringExtra(TelephonyManager.EXTRA_STATE)
        Log.d("PhoneCallReceiver", "Phone state: $state")

        when (state) {
            TelephonyManager.EXTRA_STATE_RINGING -> {
                // Get incoming number — may be null on Android 10+ without READ_CALL_LOG
                val rawNumber = intent.getStringExtra(TelephonyManager.EXTRA_INCOMING_NUMBER)
                lastIncomingNumber = rawNumber ?: "Unknown"
                lastState = state
                Log.d("PhoneCallReceiver", "RINGING from: $lastIncomingNumber")

                // Open app and show screening screen immediately when phone rings
                val launchIntent = Intent(context, MainActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP)
                    putExtra("incoming_number", lastIncomingNumber)
                }
                context.startActivity(launchIntent)
                MainActivity.onIncomingCallReceived(lastIncomingNumber ?: "Unknown")
            }

            TelephonyManager.EXTRA_STATE_OFFHOOK -> {
                // Call was answered — if we were ringing, start active WebRTC screening
                if (lastState == TelephonyManager.EXTRA_STATE_RINGING) {
                    Log.d("PhoneCallReceiver", "Call ANSWERED from: $lastIncomingNumber — starting WebRTC screening")
                    MainActivity.onCallAnswered(lastIncomingNumber ?: "Unknown")
                }
                lastState = state
            }

            TelephonyManager.EXTRA_STATE_IDLE -> {
                // Call ended
                Log.d("PhoneCallReceiver", "Call ended")
                lastState = state
                lastIncomingNumber = null
            }
        }
    }
}
