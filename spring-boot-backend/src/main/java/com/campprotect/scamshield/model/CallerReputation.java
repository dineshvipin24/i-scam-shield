package com.campprotect.scamshield.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "caller_reputation")
public class CallerReputation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "phone_number", unique = true, nullable = false)
    private String phoneNumber;

    @Column(name = "spam_reports_count")
    private Integer spamReportsCount = 0;

    @Column(name = "fraud_reports_count")
    private Integer fraudReportsCount = 0;

    @Column(name = "trust_score")
    private Integer trustScore = 100;

    @Column(name = "risk_score")
    private Integer riskScore = 0;

    @Column(name = "last_seen")
    private LocalDateTime lastSeen;

    @Column(name = "user_feedback")
    private String userFeedback;

    public CallerReputation() {
        this.lastSeen = LocalDateTime.now();
    }

    public CallerReputation(String phoneNumber) {
        this.phoneNumber = phoneNumber;
        this.lastSeen = LocalDateTime.now();
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getPhoneNumber() { return phoneNumber; }
    public void setPhoneNumber(String phoneNumber) { this.phoneNumber = phoneNumber; }

    public Integer getSpamReportsCount() { return spamReportsCount; }
    public void setSpamReportsCount(Integer spamReportsCount) { this.spamReportsCount = spamReportsCount; }

    public Integer getFraudReportsCount() { return fraudReportsCount; }
    public void setFraudReportsCount(Integer fraudReportsCount) { this.fraudReportsCount = fraudReportsCount; }

    public Integer getTrustScore() { return trustScore; }
    public void setTrustScore(Integer trustScore) { this.trustScore = trustScore; }

    public Integer getRiskScore() { return riskScore; }
    public void setRiskScore(Integer riskScore) { this.riskScore = riskScore; }

    public LocalDateTime getLastSeen() { return lastSeen; }
    public void setLastSeen(LocalDateTime lastSeen) { this.lastSeen = lastSeen; }

    public String getUserFeedback() { return userFeedback; }
    public void setUserFeedback(String userFeedback) { this.userFeedback = userFeedback; }
}
