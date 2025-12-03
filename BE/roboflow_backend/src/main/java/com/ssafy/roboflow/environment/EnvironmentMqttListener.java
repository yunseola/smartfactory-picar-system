// src/main/java/com/ssafy/roboflow/environment/EnvironmentMqttListener.java
package com.ssafy.roboflow.environment;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.eclipse.paho.client.mqttv3.*;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class EnvironmentMqttListener {

    // 여기만 final 로 남겨서 스프링이 주입하도록
    private final ObjectMapper objectMapper;
    private final EnvironmentState state;
    private final SimpMessagingTemplate messagingTemplate;

    // MqttClient 는 스프링 빈이 아니라, 내부에서 직접 생성
    private MqttClient client;

    @Value("${mqtt.username:}")
    private String username;

    @Value("${mqtt.password:}")
    private String password;

    @Value("${mqtt.enabled:true}")
    private boolean mqttEnabled;

    @Value("${mqtt.broker-url}")
    private String brokerUrl;

    @Value("${mqtt.client-id:env-listener}")
    private String clientId;

    @Value("${mqtt.topic.environment:roboflow/env}")
    private String envTopic;

    @PostConstruct
    public void subscribe() {
        // MQTT 전체를 끄고 싶을 때 (application.yml 의 mqtt.enabled=false)
        if (!mqttEnabled) {
            log.warn("[ENV] MQTT 비활성화(mqtt.enabled=false) - EnvironmentMqttListener 접속 안함");
            return;
        }

        try {
            // 여기서 직접 클라이언트 생성 & 접속
            client = new MqttClient(brokerUrl, clientId, new MemoryPersistence());

            MqttConnectOptions opts = new MqttConnectOptions();
            opts.setCleanSession(true);

            if (username != null && !username.isBlank()) {
                opts.setUserName(username);
                if (password != null) {
                    opts.setPassword(password.toCharArray());
                }
            }

            log.info("[ENV] MQTT 브로커 접속 시도: {}", brokerUrl);
            client.connect(opts);
            log.info("[ENV] MQTT 브로커 접속 성공");

            log.info("[ENV] Subscribing ENV topic: {}", envTopic);
            client.subscribe(envTopic, (topic, message) -> {
                try {
                    String payload = new String(message.getPayload(), StandardCharsets.UTF_8);
                    log.debug("[ENV] MQTT payload: {}", payload);

                    EnvironmentMqttPayload dto =
                            objectMapper.readValue(payload, EnvironmentMqttPayload.class);

                    if (dto.getTemperature() != null) {
                        state.setTemperatureC(dto.getTemperature());
                    }
                    if (dto.getHumidity() != null) {
                        state.setHumidityPct(dto.getHumidity());
                    }

                    // 상태 로그
                    log.info("[ENV] Environment updated: {}°C, {}%",
                            state.getTemperatureC(), state.getHumidityPct());

                    // STOMP 로 프론트에 브로드캐스트
                    messagingTemplate.convertAndSend(
                            "/topic/environment",
                            Map.of(
                                    "temperatureC", state.getTemperatureC(),
                                    "humidityPct", state.getHumidityPct()
                            )
                    );

                } catch (Exception e) {
                    log.error("[ENV] MQTT 환경 데이터 파싱 실패", e);
                }
            });

            log.info("[ENV] MQTT 구독 시작: {}", envTopic);

        } catch (MqttException e) {
            // 여기서 예외를 먹어버리기 때문에, 브로커가 꺼져 있어도 서버는 뜸
            log.error("[ENV] MQTT 브로커({}) 연결 실패 - 환경 실시간 업데이트는 비활성, 서버는 계속 실행",
                    brokerUrl, e);
        }
    }

    @PreDestroy
    public void disconnect() {
        try {
            if (client != null && client.isConnected()) {
                client.disconnect();
                client.close();
            }
        } catch (MqttException e) {
            log.warn("[ENV] MQTT disconnect 중 오류", e);
        }
    }
}
