package com.campprotect.scamshield.service;

import org.springframework.stereotype.Service;
import java.util.*;

@Service
public class FraudAnalysisService {

    private final List<String> keywords = Arrays.asList(
            "otp", "cvv", "pin", "aadhaar", "pan", "anydesk", "teamviewer", "quicksupport", "blocked", "lottery", "arrest", "kyc"
    );

    private final List<String> phrases = Arrays.asList(
            "share your otp", "verify your account", "install anydesk", 
            "confirm your bank details", "scan the qr code", "enter your pin"
    );

    private final List<String> intentIndicators = Arrays.asList(
            "immediately", "within 2 hours", "jail", "police department", "tax penalty", "won cash reward", "double your money"
    );

    public Map<String, Object> analyzeTranscript(String text) {
        if (text == null || text.trim().isEmpty()) {
            return getEmptyResponse();
        }

        String lowered = text.toLowerCase();
        List<String> matchedKeywords = new ArrayList<>();
        List<String> matchedPhrases = new ArrayList<>();
        List<String> matchedIntents = new ArrayList<>();

        // Layer 1: Keywords
        for (String kw : keywords) {
            if (lowered.contains(kw)) {
                matchedKeywords.add(kw);
            }
        }

        // Layer 2: Phrases
        for (String ph : phrases) {
            if (lowered.contains(ph)) {
                matchedPhrases.add(ph);
            }
        }

        // Layer 3: Intent / Urgency
        for (String intent : intentIndicators) {
            if (lowered.contains(intent)) {
                matchedIntents.add(intent);
            }
        }

        // Layer 4: Fraud Confidence Scoring (0 - 100%)
        int riskScore = 0;
        
        // Base calculation rules
        if (!matchedKeywords.isEmpty()) {
            riskScore += 25 + (matchedKeywords.size() * 5);
        }
        if (!matchedPhrases.isEmpty()) {
            riskScore += 30 + (matchedPhrases.size() * 10);
        }
        if (!matchedIntents.isEmpty()) {
            riskScore += 20 + (matchedIntents.size() * 5);
        }

        // Cap at 100
        riskScore = Math.min(riskScore, 100);

        String riskLevel = "LOW";
        String category = "Safe Call";

        if (riskScore >= 61) {
            riskLevel = "HIGH";
            category = determineCategory(lowered);
        } else if (riskScore >= 31) {
            riskLevel = "MEDIUM";
            category = "Suspicious Call";
        }

        Map<String, Object> result = new HashMap<>();
        result.put("risk_score", riskScore);
        result.put("risk_level", riskLevel);
        result.put("detected_keywords", matchedKeywords);
        result.put("detected_patterns", matchedPhrases);
        result.put("fraud_category", category);
        result.put("confidence_score", (double) riskScore / 100.0);
        result.put("evidence_report", buildEvidenceReport(riskLevel, matchedKeywords, matchedPhrases, category));

        return result;
    }

    private String determineCategory(String text) {
        if (text.contains("otp")) return "OTP Scam";
        if (text.contains("anydesk") || text.contains("teamviewer")) return "Remote Access Scam";
        if (text.contains("kyc") || text.contains("aadhaar") || text.contains("pan")) return "KYC Scam";
        if (text.contains("lottery") || text.contains("won")) return "Lottery Scam";
        if (text.contains("police") || text.contains("arrest") || text.contains("tax")) return "Government Scam";
        if (text.contains("pin") || text.contains("upi") || text.contains("qr")) return "UPI Scam";
        return "Banking Scam";
    }

    private String buildEvidenceReport(String level, List<String> kws, List<String> phs, String category) {
        if ("LOW".equals(level)) {
            return "No prominent threat indicators detected.";
        }
        return String.format("Call transcript flagged as %s RISK. Key terms identified: %s. Phrase patterns matched: %s. Matches %s profile signature.", 
                level, kws.toString(), phs.toString(), category);
    }

    private Map<String, Object> getEmptyResponse() {
        Map<String, Object> result = new HashMap<>();
        result.put("risk_score", 0);
        result.put("risk_level", "LOW");
        result.put("detected_keywords", Collections.emptyList());
        result.put("detected_patterns", Collections.emptyList());
        result.put("fraud_category", "Safe Call");
        result.put("confidence_score", 0.0);
        result.put("evidence_report", "Empty transcript evaluated.");
        return result;
    }
}
