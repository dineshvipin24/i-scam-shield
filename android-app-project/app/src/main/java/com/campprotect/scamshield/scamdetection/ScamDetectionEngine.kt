package com.campprotect.scamshield.scamdetection

import java.util.Locale

class ScamDetectionEngine {

    // Layer 1: Keyword Weights
    private val keywordWeights = mapOf(
        "otp" to 30,
        "cvv" to 50,
        "upi pin" to 50,
        "aadhaar" to 20,
        "aadhar" to 20,
        "pan" to 20,
        "anydesk" to 70,
        "teamviewer" to 70,
        "remote access" to 70,
        "kyc update" to 20,
        "bank account" to 30,
        "debit card" to 30,
        "credit card" to 30
    )

    // Layer 2: Phrase Pattern Weights (Indicate direct requests or action items)
    private val phrasePatternWeights = mapOf(
        "share your otp" to 50,
        "verify your account" to 40,
        "install anydesk" to 80,
        "install teamviewer" to 80,
        "bank verification" to 40,
        "send upi pin" to 60,
        "card details" to 40,
        "confirm password" to 50,
        "verify kyc" to 40
    )

    data class DetectionResult(
        val confidenceScore: Int, // 0 - 100
        val riskLevel: RiskLevel,
        val category: String, // Layer 3: Category classification
        val matchedKeywords: List<String>,
        val matchedPhrases: List<String>
    )

    enum class RiskLevel {
        LOW,    // 0 - 30
        MEDIUM, // 31 - 60
        HIGH    // 61+
    }

    /**
     * Conducts 4-layer hybrid evaluation of conversation transcripts
     */
    fun evaluateTranscript(transcript: String): DetectionResult {
        val lowerText = transcript.toLowerCase(Locale.getDefault())
        val matchedKeywords = mutableListOf<String>()
        val matchedPhrases = mutableListOf<String>()
        
        var totalScore = 0

        // Layer 1: Keyword Detection
        for ((keyword, weight) in keywordWeights) {
            if (lowerText.contains(keyword)) {
                matchedKeywords.add(keyword)
                totalScore += weight
            }
        }

        // Layer 2: Phrase Detection
        for ((phrase, weight) in phrasePatternWeights) {
            if (lowerText.contains(phrase)) {
                matchedPhrases.add(phrase)
                totalScore += weight
            }
        }

        // Layer 3: Context Detection & Classification
        val category = classifyContext(lowerText, matchedKeywords, matchedPhrases)

        // Layer 4: Confidence Score Calculation (normalized and capped at 100)
        val confidenceScore = Math.min(totalScore, 100)

        val riskLevel = when {
            confidenceScore >= 61 -> RiskLevel.HIGH
            confidenceScore >= 31 -> RiskLevel.MEDIUM
            else -> RiskLevel.LOW
        }

        return DetectionResult(
            confidenceScore = confidenceScore,
            riskLevel = riskLevel,
            category = category,
            matchedKeywords = matchedKeywords,
            matchedPhrases = matchedPhrases
        )
    }

    private fun classifyContext(text: String, keywords: List<String>, phrases: List<String>): String {
        // Evaluate context categories based on matches and frequency
        val isRemoteAccess = text.contains("anydesk") || text.contains("teamviewer") || text.contains("remote access")
        val isBanking = text.contains("bank") || text.contains("card") || text.contains("cvv") || text.contains("verification")
        val isGov = text.contains("aadhaar") || text.contains("aadhar") || text.contains("pan") || text.contains("kyc")
        val isLottery = text.contains("lottery") || text.contains("prize") || text.contains("won") || text.contains("free")

        return when {
            isRemoteAccess -> "Remote Access Scam"
            isBanking -> "Banking Scam"
            isGov -> "Government/KYC Impersonation"
            isLottery -> "Lottery/Reward Scam"
            keywords.isNotEmpty() || phrases.isNotEmpty() -> "Suspicious Behavior"
            else -> "Safe Call"
        }
    }
}
