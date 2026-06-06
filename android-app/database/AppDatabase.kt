package com.campprotect.scamshield.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [
        CallHistory::class, 
        FraudAlertLog::class, 
        CallerReputation::class, 
        UserSettings::class
    ], 
    version = 1, 
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {

    abstract fun callHistoryDao(): CallHistoryDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "scam_shield_production_db"
                )
                .fallbackToDestructiveMigration() // Simple strategy for student project iterations
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
