// src/main/java/com/ssafy/roboflow/environment/EnvironmentController.java
package com.ssafy.roboflow.environment;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/environment")
@RequiredArgsConstructor
public class EnvironmentController {

    private final EnvironmentState state;
    private final SimpMessagingTemplate messagingTemplate; // 👈 STOMP 브로드캐스트용

    @GetMapping
    public ResponseEntity<Map<String, Object>> getEnvironmentData() {
        return ResponseEntity.ok(
                Map.of(
                        "temperatureC", state.getTemperatureC(),
                        "humidityPct", state.getHumidityPct()
                )
        );
    }

    /**
     * 🔹 Postman으로 온도/습도 값을 넣어서 강제로 상태를 바꾸는 테스트용 엔드포인트
     *    - 요청 바디: { "temperature": 25.3, "humidity": 40.0 }
     */
    @PostMapping("/mock")
    public ResponseEntity<Map<String, Object>> updateEnvironment(@RequestBody EnvironmentMqttPayload payload) {

        if (payload.getTemperature() != null) {
            state.setTemperatureC(payload.getTemperature());
        }
        if (payload.getHumidity() != null) {
            state.setHumidityPct(payload.getHumidity());
        }

        // 현재 상태
        Map<String, Object> body = Map.of(
                "temperatureC", state.getTemperatureC(),
                "humidityPct", state.getHumidityPct()
        );

        // 👉 프론트로도 STOMP 브로드캐스트 (실제 MQTT 들어온 것처럼 동작)
        messagingTemplate.convertAndSend("/topic/environment", body);

        return ResponseEntity.ok(body);
    }
}
