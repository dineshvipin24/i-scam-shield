package com.campprotect.scamshield.service;

import com.campprotect.scamshield.model.CallLog;
import com.campprotect.scamshield.repository.CallLogRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.socket.CloseStatus;
import org.springframework.web.socket.TextMessage;
import org.springframework.web.socket.WebSocketSession;
import org.springframework.web.socket.handler.TextWebSocketHandler;
import java.io.IOException;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class WebRtcSignalingHandler extends TextWebSocketHandler {

    private final Map<String, WebSocketSession> sessions = new ConcurrentHashMap<>();
    private final Map<String, CallLog> activeCallLogs = new ConcurrentHashMap<>();
    private final ObjectMapper mapper = new ObjectMapper();

    @Autowired
    private FraudAnalysisService fraudService;

    @Autowired
    private CallLogRepository callLogRepository;

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        sessions.put(session.getId(), session);
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message) throws IOException {
        String payload = message.getPayload();
        Map<String, Object> data = mapper.readValue(payload, Map.class);
        String event = (String) data.get("event");

        switch (event) {
            case "start":
                handleStart(session, data);
                break;
            case "sdp_offer":
                handleSdpOffer(session, data);
                break;
            case "ice_candidate":
                handleIceCandidate(session, data);
                break;
            case "speech_chunk":
                handleSpeechChunk(session, data);
                break;
            case "stop":
                handleStop(session);
                break;
            default:
                System.out.println("[WebRTC Signaling] Unknown event: " + event);
        }
    }

    private void handleStart(WebSocketSession session, Map<String, Object> data) {
        Map<String, Object> details = (Map<String, Object>) data.get("start");
        String callSid = (String) details.get("callSid");
        String callerNumber = (String) details.get("callerNumber");

        CallLog log = new CallLog(callSid, callerNumber, "", 0, "Safe Call");
        callLogRepository.save(log);
        activeCallLogs.put(session.getId(), log);
        
        System.out.println("[WebRTC] Screening call started: " + callSid + " from " + callerNumber);
    }

    private void handleSdpOffer(WebSocketSession session, Map<String, Object> data) throws IOException {
        String sdp = (String) data.get("sdp");
        // Simulated local SDP Answer (standard placeholder loopback)
        Map<String, Object> answer = Map.of(
            "event", "sdp_answer",
            "type", "answer",
            "sdp", sdp
        );
        session.sendMessage(new TextMessage(mapper.writeValueAsString(answer)));
    }

    private void handleIceCandidate(WebSocketSession session, Map<String, Object> data) {
        // Log candidate info
    }

    private void handleSpeechChunk(WebSocketSession session, Map<String, Object> data) throws IOException {
        String transcriptText = (String) data.get("text");
        CallLog log = activeCallLogs.get(session.getId());

        if (log != null) {
            String updatedTranscript = log.getTranscript() + " " + transcriptText;
            log.setTranscript(updatedTranscript.trim());

            // Run analysis
            Map<String, Object> analysis = fraudService.analyzeTranscript(log.getTranscript());
            log.setScamRiskScore((Integer) analysis.get("risk_score"));
            log.setCategory((String) analysis.get("fraud_category"));
            callLogRepository.save(log);

            // Broadcast real-time update back to app
            Map<String, Object> updateMsg = Map.of(
                "event", "call_update",
                "data", analysis
            );
            session.sendMessage(new TextMessage(mapper.writeValueAsString(updateMsg)));
        }
    }

    private void handleStop(WebSocketSession session) throws IOException {
        activeCallLogs.remove(session.getId());
        session.close();
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        sessions.remove(session.getId());
        activeCallLogs.remove(session.getId());
    }
}
