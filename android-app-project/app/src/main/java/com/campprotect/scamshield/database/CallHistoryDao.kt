package com.campprotect.scamshield.database

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update

@Dao
interface CallHistoryDao {
    
    // CallHistory
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCall(call: CallHistory): Long

    @Query("SELECT * FROM CallHistory ORDER BY timestamp DESC")
    suspend fun getAllCalls(): List<CallHistory>

    @Query("DELETE FROM CallHistory")
    suspend fun clearAllCalls()

    // FraudAlertLog
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAlertLog(log: FraudAlertLog): Long

    @Query("SELECT * FROM FraudAlertLog ORDER BY timestamp DESC")
    suspend fun getAllAlertLogs(): List<FraudAlertLog>

    @Query("SELECT * FROM FraudAlertLog WHERE id = :logId")
    suspend fun getAlertLogById(logId: Long): FraudAlertLog?

    @Query("DELETE FROM FraudAlertLog")
    suspend fun clearAllAlertLogs()

    // CallerReputation
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrUpdateReputation(reputation: CallerReputation): Long

    @Query("SELECT * FROM CallerReputation WHERE phoneNumber = :phone")
    suspend fun getReputationByNumber(phone: String): CallerReputation?

    @Query("SELECT * FROM CallerReputation ORDER BY spamReportsCount DESC")
    suspend fun getAllReputations(): List<CallerReputation>

    // UserSettings (Single row configuration, id = 1)
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun saveSettings(settings: UserSettings)

    @Query("SELECT * FROM UserSettings WHERE id = 1")
    suspend fun getSettings(): UserSettings?
}
