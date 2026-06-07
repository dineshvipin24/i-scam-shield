package com.campprotect.scamshield.database

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "CallHistory")
data class CallHistory(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val phoneNumber: String,
    val timestamp: Long,
    val transcript: String,
    val riskScore: Int, // 0-100
    val riskLevel: String, // "LOW", "MEDIUM", "HIGH"
    val classification: String // e.g., "Banking Scam", "OTP Phishing", "Safe Call"
)
