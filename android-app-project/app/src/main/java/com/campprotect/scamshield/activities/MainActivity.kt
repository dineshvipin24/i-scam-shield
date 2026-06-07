package com.campprotect.scamshield.activities

import android.app.role.RoleManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.lifecycle.lifecycleScope
import com.campprotect.scamshield.database.AppDatabase
import com.campprotect.scamshield.database.CallHistory
import com.campprotect.scamshield.database.CallerReputation
import com.campprotect.scamshield.database.FraudAlertLog
import com.campprotect.scamshield.database.UserSettings
import com.campprotect.scamshield.repository.CallHistoryRepository
import com.campprotect.scamshield.services.CallMonitoringForegroundService
import com.campprotect.scamshield.ui.HomeScreen
import com.campprotect.scamshield.ui.PrivacyDashboardScreen
import androidx.compose.runtime.collectAsState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {

    private val TAG = "MainActivity"
    private val REQUEST_OVERLAY_PERMISSION = 3001
    private val REQUEST_SCREENING_ROLE = 3002

    lateinit var repository: CallHistoryRepository

    // State Flows for UI binding
    val isMonitoringState = MutableStateFlow(false)
    val activeNumberState = MutableStateFlow("")
    val liveScoreState = MutableStateFlow(0)
    val liveCategoryState = MutableStateFlow("Safe Call")
    val livePhraseState = MutableStateFlow("")

    val callLogsState = MutableStateFlow<List<CallHistory>>(emptyList())
    val alertLogsState = MutableStateFlow<List<FraudAlertLog>>(emptyList())
    val reputationState = MutableStateFlow<List<CallerReputation>>(emptyList())
    val settingsState = MutableStateFlow(UserSettings())

    // Consent gating state
    val consentAcceptedState = MutableStateFlow(false)

    private val monitorReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            when (intent?.action) {
                "com.campprotect.scamshield.MONITOR_STATUS" -> {
                    val active = intent.getBooleanExtra("ACTIVE", false)
                    val phone = intent.getStringExtra("PHONE") ?: ""
                    isMonitoringState.value = active
                    activeNumberState.value = phone
                    if (!active) {
                        // Reset live state
                        liveScoreState.value = 0
                        liveCategoryState.value = "Safe Call"
                        livePhraseState.value = ""
                    }
                    refreshData()
                }
                "com.campprotect.scamshield.SCAM_UPDATE" -> {
                    val score = intent.getIntExtra("SCORE", 0)
                    val phrase = intent.getStringExtra("PHRASE") ?: ""
                    val category = intent.getStringExtra("CATEGORY") ?: "Suspicious Call"
                    
                    liveScoreState.value = score
                    livePhraseState.value = phrase
                    liveCategoryState.value = category
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialize Repository
        val database = AppDatabase.getDatabase(this)
        repository = CallHistoryRepository(database.callHistoryDao())

        // Read consent preference
        val sharedPrefs = getSharedPreferences("CampProtectPrefs", Context.MODE_PRIVATE)
        consentAcceptedState.value = sharedPrefs.getBoolean("pref_consent_accepted", false)

        refreshData()

        setContent {
            val consentAccepted = consentAcceptedState.collectAsState().value
            if (!consentAccepted) {
                // Render custom Prominent Disclosure screen
                PrivacyDashboardScreen(
                    onAccept = {
                        sharedPrefs.edit().putBoolean("pref_consent_accepted", true).apply()
                        consentAcceptedState.value = true
                        checkAndRequestPermissions()
                    },
                    onDecline = {
                        finish() // Comply with policy: Close app if consent is declined
                    }
                )
            } else {
                // Main Application UI
                HomeScreen(
                    activity = this,
                    isMonitoring = isMonitoringState,
                    activeNumber = activeNumberState,
                    liveScore = liveScoreState,
                    liveCategory = liveCategoryState,
                    livePhrase = livePhraseState,
                    callHistory = callLogsState,
                    alertLogs = alertLogsState,
                    reputationLogs = reputationState
                )
            }
        }

        // Register monitor events receiver
        val filter = IntentFilter().apply {
            addAction("com.campprotect.scamshield.MONITOR_STATUS")
            addAction("com.campprotect.scamshield.SCAM_UPDATE")
        }
        registerReceiver(monitorReceiver, filter)
    }

    fun refreshData() {
        lifecycleScope.launch {
            callLogsState.value = repository.getAllCalls()
            alertLogsState.value = repository.getAllAlertLogs()
            reputationState.value = repository.getAllReputations()
            settingsState.value = repository.getSettings() ?: UserSettings()
        }
    }

    fun checkAndRequestPermissions() {
        // Overlay permission justification check
        if (!Settings.canDrawOverlays(this)) {
            val intent = Intent(
                Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                Uri.parse("package:$packageName")
            )
            startActivityForResult(intent, REQUEST_OVERLAY_PERMISSION)
        }

        // Default screening role requirement (Android 10+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val roleManager = getSystemService(Context.ROLE_SERVICE) as RoleManager
            if (!roleManager.isRoleHeld(RoleManager.ROLE_CALL_SCREENING)) {
                val intent = roleManager.createRequestRoleIntent(RoleManager.ROLE_CALL_SCREENING)
                startActivityForResult(intent, REQUEST_SCREENING_ROLE)
            }
        }

        // Runtime Recording permission (Requested after prominent disclosure)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            requestPermissions(
                arrayOf(
                    android.Manifest.permission.RECORD_AUDIO,
                    android.Manifest.permission.READ_PHONE_STATE,
                    android.Manifest.permission.ANSWER_PHONE_CALLS
                ),
                3003
            )
        }
    }

    /**
     * Diagnostic testing utility to start monitoring programmatically (e.g. for student presentation tests).
     */
    fun startTestMonitoring(phoneNumber: String) {
        val intent = Intent(this, CallMonitoringForegroundService::class.java).apply {
            putExtra("EXTRA_PHONE_NUMBER", phoneNumber)
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
    }

    fun stopTestMonitoring() {
        val intent = Intent(this, CallMonitoringForegroundService::class.java)
        stopService(intent)
    }

    override fun onDestroy() {
        super.onDestroy()
        unregisterReceiver(monitorReceiver)
    }
}
