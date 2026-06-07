package com.campprotect.scamshield.repository

import com.campprotect.scamshield.database.CallHistory
import com.campprotect.scamshield.database.CallHistoryDao
import com.campprotect.scamshield.database.CallerReputation
import com.campprotect.scamshield.database.FraudAlertLog
import com.campprotect.scamshield.database.UserSettings
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class CallHistoryRepository(private val dao: CallHistoryDao) {

    // Call History Operations
    suspend fun insertCall(call: CallHistory): Long = withContext(Dispatchers.IO) {
        dao.insertCall(call)
    }

    suspend fun getAllCalls(): List<CallHistory> = withContext(Dispatchers.IO) {
        dao.getAllCalls()
    }

    suspend fun clearAllCalls() = withContext(Dispatchers.IO) {
        dao.clearAllCalls()
    }

    // Fraud Alert Log Operations
    suspend fun insertAlertLog(log: FraudAlertLog): Long = withContext(Dispatchers.IO) {
        dao.insertAlertLog(log)
    }

    suspend fun getAllAlertLogs(): List<FraudAlertLog> = withContext(Dispatchers.IO) {
        dao.getAllAlertLogs()
    }

    suspend fun getAlertLogById(logId: Long): FraudAlertLog? = withContext(Dispatchers.IO) {
        dao.getAlertLogById(logId)
    }

    suspend fun clearAllAlertLogs() = withContext(Dispatchers.IO) {
        dao.clearAllAlertLogs()
    }

    // Caller Reputation Operations
    suspend fun insertOrUpdateReputation(reputation: CallerReputation): Long = withContext(Dispatchers.IO) {
        dao.insertOrUpdateReputation(reputation)
    }

    suspend fun getReputationByNumber(phone: String): CallerReputation? = withContext(Dispatchers.IO) {
        dao.getReputationByNumber(phone)
    }

    suspend fun getAllReputations(): List<CallerReputation> = withContext(Dispatchers.IO) {
        dao.getAllReputations()
    }

    // User Settings Operations
    suspend fun saveSettings(settings: UserSettings) = withContext(Dispatchers.IO) {
        dao.saveSettings(settings)
    }

    suspend fun getSettings(): UserSettings? = withContext(Dispatchers.IO) {
        dao.getSettings()
    }
}
