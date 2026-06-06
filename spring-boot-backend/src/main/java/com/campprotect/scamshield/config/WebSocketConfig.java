package com.campprotect.scamshield.config;

import com.campprotect.scamshield.service.WebRtcSignalingHandler;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.socket.config.annotation.*;

@Configuration
@EnableWebSocket
public class WebSocketConfig implements WebSocketConfigurer {

    @Autowired
    private WebRtcSignalingHandler signalingHandler;

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        // Register WebRTC socket endpoint and allow cross-origin requests
        registry.addHandler(signalingHandler, "/stream/webrtc")
                .setAllowedOrigins("*");
    }
}
