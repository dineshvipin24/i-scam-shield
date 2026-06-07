package com.campprotect.scamshield.database

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "FraudAlertLog")
data class FraudAlertLog(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val phoneNumber: String,
    val timestamp: Long,
    val riskScore: Int,
    val triggerKeyword: String,
    val alertType: String, // "LOW", "MEDIUM", "HIGH"
    val transcriptSnippet: String,
    val category: String // e.g., "Lottery Scam", "Government Impersonation"
)
