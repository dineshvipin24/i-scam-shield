package com.campprotect.scamshield.database

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "UserSettings")
data class UserSettings(
    @PrimaryKey val id: Int = 1, // Single-row configuration structure
    val saveCallHistory: Boolean = true,
    val enableBeep: Boolean = true,
    val enableVibration: Boolean = true,
    val enableTTS: Boolean = true,
    val alertVolume: Float = 0.8f
)
