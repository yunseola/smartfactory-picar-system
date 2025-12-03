package com.ssafy.roboflow.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.ssafy.roboflow.eventlog.EventLogInputDto;
import com.ssafy.roboflow.eventlog.EventlogService;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.eclipse.paho.client.mqttv3.*;
import org.eclipse.paho.client.mqttv3.persist.MemoryPersistence;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Slf4j
@Service
@RequiredArgsConstructor
public class MqttEventlogListener {

    private final EventlogService eventlogService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    private MqttClient client;

    @Value("${mqtt.broker-url}")
    private String brokerUrl;      // 예: tcp://192.168.0.10:1883

    @Value("${mqtt.client-id:eventlog-listener}")
    private String clientId;

    @Value("${mqtt.topic.eventlog:roboflow/eventlog}")
    private String eventlogTopic;

    @Value("${mqtt.enabled:true}")
    private boolean mqttEnabled;

    @PostConstruct
    public void connect() {
        if (!mqttEnabled) {
            log.warn("MQTT 비활성화됨 (mqtt.enabled=false) - broker 연결/구독 생략");
            return;
        }

        try {
            client = new MqttClient(brokerUrl, clientId, new MemoryPersistence());

            MqttConnectOptions opts = new MqttConnectOptions();
            opts.setCleanSession(true);

            log.info("Connecting to MQTT broker: {}", brokerUrl);
            client.connect(opts);
            log.info("Connected to MQTT broker.");

            client.subscribe(eventlogTopic, (topic, message) -> {
                String payload = new String(message.getPayload());
                log.info("MQTT Eventlog message received: {}", payload);
                try {
                    EventLogInputDto dto =
                            objectMapper.readValue(payload, EventLogInputDto.class);
                    eventlogService.append(dto);   // DB 저장 + STOMP 브로드캐스트
                } catch (Exception e) {
                    log.error("Failed to handle MQTT eventlog payload", e);
                }
            });

            log.info("Subscribed to topic: {}", eventlogTopic);

        } catch (MqttException e) {
            // 👉 여기서 예외를 잡아먹기 때문에 main까지 안 올라감
            log.error("❌ MQTT broker({}) 연결 실패 - MQTT eventlog 수신 없이 애플리케이션 계속 실행합니다.",
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
            log.warn("Error while disconnecting MQTT client", e);
        }
    }
}
