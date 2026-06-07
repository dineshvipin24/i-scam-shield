package com.campprotect.scamshield.activities

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.lifecycle.lifecycleScope
import com.campprotect.scamshield.database.AppDatabase
import com.campprotect.scamshield.database.UserSettings
import com.campprotect.scamshield.overlay.FraudAlertManager
import com.campprotect.scamshield.repository.CallHistoryRepository
import com.campprotect.scamshield.ui.SettingsScreen
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.launch

class SettingsActivity : ComponentActivity() {

    private lateinit var alertManager: FraudAlertManager
    private lateinit var repository: CallHistoryRepository
    
    val settingsState = MutableStateFlow(UserSettings())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        val database = AppDatabase.getDatabase(this)
        repository = CallHistoryRepository(database.callHistoryDao())
        alertManager = FraudAlertManager(this)

        loadSettings()

        setContent {
            SettingsScreen(
                activity = this,
                settings = settingsState,
                onSave = { updatedSettings ->
                    saveSettings(updatedSettings)
                },
                onTestBeep = {
                    alertManager.playWarningBeep()
                },
                onTestAlarm = {
                    alertManager.playFraudAlarm()
                    Handler(Looper.getMainLooper()).postDelayed({
                        alertManager.stopAlarm()
                    }, 3000)
                }
            )
        }
    }

    private fun loadSettings() {
        lifecycleScope.launch {
            val config = repository.getSettings() ?: UserSettings()
            settingsState.value = config
        }
    }

    private fun saveSettings(updated: UserSettings) {
        lifecycleScope.launch {
            repository.saveSettings(updated)
            settingsState.value = updated
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        alertManager.destroy()
    }
}
