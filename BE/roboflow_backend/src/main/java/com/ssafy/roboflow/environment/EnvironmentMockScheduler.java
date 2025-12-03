// src/main/java/com/ssafy/roboflow/environment/EnvironmentMockScheduler.java
package com.ssafy.roboflow.environment;

import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.Map;

/**
 * 센서/임베디드가 아직 없을 때 사용하는
 * 온도/습도 하드코딩 시뮬레이터.
 *
 * 10초마다:
 *   온도: 24 ↔ 25
 *   습도: 68 ↔ 70
 * 로 변경하고 /topic/environment 로 STOMP 브로드캐스트.
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class EnvironmentMockScheduler {

    private final EnvironmentState state;
    private final SimpMessagingTemplate messagingTemplate;

    private boolean toggle = false;

    @PostConstruct
    public void init() {
        log.info("[ENV-MOCK] EnvironmentMockScheduler 활성화됨 (10초마다 온/습도 변경)");
    }

    @Scheduled(fixedRate = 10_000)
    public void tick() {
        toggle = !toggle;

        double temp = toggle ? 24.0 : 25.0;
        double humid = toggle ? 68.0 : 70.0;

        state.setTemperatureC(temp);
        state.setHumidityPct(humid);

        log.info("[ENV-MOCK] temp={}°C, humidity={}%", temp, humid);

        // STOMP 브로드캐스트
        messagingTemplate.convertAndSend(
                "/topic/environment",
                Map.of(
                        "temperatureC", state.getTemperatureC(),
                        "humidityPct", state.getHumidityPct()
                )
        );
    }
}
