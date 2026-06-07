package com.campprotect.scamshield.scamdetection

import com.campprotect.scamshield.database.CallerReputation

class CallerReputationEngine {

    /**
     * Calculates base reputation score for incoming numbers.
     * Rules:
     * - Contact Saved = 0 Risk
     * - Unknown Number = +10 Risk
     * - Previously Reported Spam = +40 Risk
     * - User Marked Safe = Reduces Risk
     * - User Marked Scam = Increases Risk
     */
    fun calculateBaseReputationRisk(
        isContactSaved: Boolean,
        reputationRecord: CallerReputation?
    ): Int {
        if (isContactSaved) {
            return 0 // Trust saved contacts completely
        }

        var baseRisk = 10 // Start with +10 for unknown numbers

        reputationRecord?.let { record ->
            // If previously reported or marked as scam
            if (record.spamReportsCount > 0 || record.scamReportsCount > 0) {
                baseRisk += 40
            }

            // Adjust based on manual user feedback
            when (record.userFeedbackValue) {
                "SCAM" -> baseRisk += 30
                "SAFE" -> baseRisk -= 20
            }

            // Apply specific weights based on report counts
            baseRisk += (record.spamReportsCount * 5) + (record.scamReportsCount * 10)
        }

        // Return bounded risk value between 0 and 100
        return Math.max(0, Math.min(baseRisk, 100))
    }
}
