package com.campprotect.scamshield.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "call_logs")
public class CallLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "call_sid", unique = true, nullable = false)
    private String callSid;

    @Column(name = "caller_number", nullable = false)
    private String callerNumber;

    @Column(columnDefinition = "TEXT")
    private String transcript;

    @Column(name = "scam_risk_score")
    private Integer scamRiskScore;

    private String category;

    private LocalDateTime timestamp;

    public CallLog() {
        this.timestamp = LocalDateTime.now();
    }

    public CallLog(String callSid, String callerNumber, String transcript, Integer scamRiskScore, String category) {
        this.callSid = callSid;
        this.callerNumber = callerNumber;
        this.transcript = transcript;
        this.scamRiskScore = scamRiskScore;
        this.category = category;
        this.timestamp = LocalDateTime.now();
    }

    // Getters and Setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getCallSid() { return callSid; }
    public void setCallSid(String callSid) { this.callSid = callSid; }

    public String getCallerNumber() { return callerNumber; }
    public void setCallerNumber(String callerNumber) { this.callerNumber = callerNumber; }

    public String getTranscript() { return transcript; }
    public void setTranscript(String transcript) { this.transcript = transcript; }

    public Integer getScamRiskScore() { return scamRiskScore; }
    public void setScamRiskScore(Integer scamRiskScore) { this.scamRiskScore = scamRiskScore; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public LocalDateTime getTimestamp() { return timestamp; }
    public void setTimestamp(LocalDateTime timestamp) { this.timestamp = timestamp; }
}
