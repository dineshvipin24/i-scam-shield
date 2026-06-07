package com.campprotect.scamshield.database

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "CallerReputation")
data class CallerReputation(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val phoneNumber: String,
    val spamReportsCount: Int,
    val scamReportsCount: Int,
    val localRiskScore: Int, // Calculated reputation score
    val lastSeenTimestamp: Long,
    val userFeedbackValue: String, // "SAFE", "SCAM", "NONE"
    val isSafe: Boolean
)
