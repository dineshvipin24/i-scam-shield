package com.campprotect.scamshield.controller;

import com.campprotect.scamshield.model.CallLog;
import com.campprotect.scamshield.model.CallerReputation;
import com.campprotect.scamshield.repository.CallLogRepository;
import com.campprotect.scamshield.repository.ReputationRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.time.LocalDateTime;
import java.util.*;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class CallController {

    @Autowired
    private CallLogRepository callLogRepository;

    @Autowired
    private ReputationRepository reputationRepository;

    // Get all call logs
    @GetMapping("/calls")
    public List<CallLog> getCallLogs() {
        return callLogRepository.findAll();
    }

    // Get specific caller reputation status
    @GetMapping("/reputation/{number}")
    public ResponseEntity<CallerReputation> getReputation(@PathVariable String number) {
        CallerReputation rep = reputationRepository.findByPhoneNumber(number)
                .orElseGet(() -> {
                    CallerReputation newRep = new CallerReputation(number);
                    return reputationRepository.save(newRep);
                });
        return ResponseEntity.ok(rep);
    }

    // Report spam or fraud attempt
    @PostMapping("/reputation/report")
    public ResponseEntity<CallerReputation> reportNumber(
            @RequestParam String number,
            @RequestParam String type,
            @RequestParam(required = false) String feedback) {
        
        CallerReputation rep = reputationRepository.findByPhoneNumber(number)
                .orElse(new CallerReputation(number));

        if ("spam".equalsIgnoreCase(type)) {
            rep.setSpamReportsCount(rep.getSpamReportsCount() + 1);
            rep.setRiskScore(Math.min(rep.getRiskScore() + 10, 100));
        } else if ("fraud".equalsIgnoreCase(type)) {
            rep.setFraudReportsCount(rep.getFraudReportsCount() + 1);
            rep.setRiskScore(Math.min(rep.getRiskScore() + 40, 100));
        }
        
        // Trust score is the inverse of risk
        rep.setTrustScore(100 - rep.getRiskScore());
        rep.setLastSeen(LocalDateTime.now());
        if (feedback != null) {
            rep.setUserFeedback(feedback);
        }

        CallerReputation updated = reputationRepository.save(rep);
        return ResponseEntity.ok(updated);
    }

    // Mock settings config
    @GetMapping("/settings")
    public ResponseEntity<Map<String, Object>> getSettings() {
        return ResponseEntity.ok(Map.of(
            "enableLocalFiltering", true,
            "enableCloudAnalytics", true,
            "minRiskLevelAlert", 30
        ));
    }

    @PostMapping("/settings")
    public ResponseEntity<Map<String, Object>> updateSettings(@RequestBody Map<String, Object> settings) {
        return ResponseEntity.ok(settings);
    }
}
