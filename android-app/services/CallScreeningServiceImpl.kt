package com.campprotect.scamshield.services

import android.content.Context
import android.content.Intent
import android.os.Build
import android.telecom.Call
import android.telecom.CallScreeningService
import android.telephony.PhoneStateListener
import android.telephony.TelephonyManager
import android.util.Log
import androidx.annotation.RequiresApi
import com.campprotect.scamshield.database.AppDatabase
import com.campprotect.scamshield.scamdetection.CallerReputationEngine
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

@RequiresApi(Build.VERSION_CODES.Q)
class CallScreeningServiceImpl : CallScreeningService() {

    private val TAG = "CallScreeningService"
    private val reputationEngine = CallerReputationEngine()

    override fun onScreenCall(callDetails: Call.Details) {
        val rawNumber = callDetails.handle?.schemeSpecificPart ?: ""
        Log.d(TAG, "Incoming call screened: $rawNumber")

        val sharedPrefs = getSharedPreferences("CampProtectPrefs", Context.MODE_PRIVATE)
        sharedPrefs.edit().putString("active_incoming_number", rawNumber).apply()

        // Fetch reputation and determine baseline risk asynchronously
        CoroutineScope(Dispatchers.IO).launch {
            val db = AppDatabase.getDatabase(applicationContext)
            val record = db.callHistoryDao().getReputationByNumber(rawNumber)
            
            // Assume not saved in local system contacts for screening triggers
            val baseReputationRisk = reputationEngine.calculateBaseReputationRisk(
                isContactSaved = false,
                reputationRecord = record
            )
            
            sharedPrefs.edit().putInt("active_number_reputation_risk", baseReputationRisk).apply()
            Log.d(TAG, "Number: $rawNumber calculated baseline reputation threat: +$baseReputationRisk")
        }

        // Register listener for answered transition
        listenForCallState(rawNumber)

        // Allow the call to connect normally
        val response = CallResponse.Builder()
            .setDisallowCall(false)
            .setRejectCall(false)
            .setSilenceCall(false)
            .setSkipCallLog(false)
            .setSkipNotification(false)
            .build()

        respondToCall(callDetails, response)
    }

    private fun listenForCallState(phoneNumber: String) {
        val telephonyManager = getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
        val listener = object : PhoneStateListener() {
            @Deprecated("Deprecated in Java")
            override fun onCallStateChanged(state: Int, incomingNumber: String?) {
                super.onCallStateChanged(state, incomingNumber)
                when (state) {
                    TelephonyManager.CALL_STATE_OFFHOOK -> {
                        Log.d(TAG, "Call Answered. Directing Foreground Service launch.")
                        
                        // Launch compliant Foreground Service of type 'microphone'
                        val startIntent = Intent(applicationContext, CallMonitoringForegroundService::class.java).apply {
                            putExtra("EXTRA_PHONE_NUMBER", phoneNumber)
                        }
                        
                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                            startForegroundService(startIntent)
                        } else {
                            startService(startIntent)
                        }
                    }
                    TelephonyManager.CALL_STATE_IDLE -> {
                        Log.d(TAG, "Call Idle. Terminating Foreground Service monitoring.")
                        val stopIntent = Intent(applicationContext, CallMonitoringForegroundService::class.java)
                        stopService(stopIntent)
                        
                        // Detach listener
                        telephonyManager.listen(this, LISTEN_NONE)
                    }
                }
            }
        }
        telephonyManager.listen(listener, PhoneStateListener.LISTEN_CALL_STATE)
    }
}
