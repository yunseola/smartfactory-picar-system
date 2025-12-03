// src/main/java/com/ssafy/roboflow/config/WebSocketConfig.java
package com.ssafy.roboflow.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;

@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws")
                // 개발용: 로컬 + EC2/SSAFY 도메인 모두 허용
                .setAllowedOriginPatterns(
                        "http://localhost:3000",
                        "http://k13e103.p.ssafy.io",
                        "https://k13e103.p.ssafy.io",
                        "*"
                )
                .withSockJS();   // SockJS 사용 (그래서 /ws/info 로 요청이 감)
    }

    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        // 서버 -> 클라 브로드캐스트 주소
        registry.enableSimpleBroker("/topic");

        // 클라 -> 서버 보낼 때 prefix (예: /app/xxx)
        registry.setApplicationDestinationPrefixes("/app");
    }
}
