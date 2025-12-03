// src/main/java/com/ssafy/roboflow/environment/EnvironmentState.java
package com.ssafy.roboflow.environment;

import lombok.Getter;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
@Getter
public class EnvironmentState {

    // 마지막으로 받은 값
    private volatile double temperatureC = 0.0;
    private volatile double humidityPct = 0.0;

    // 마지막 업데이트 시각
    private volatile Instant lastUpdated = null;

    /** 온도만 갱신될 때 호출 */
    public void setTemperatureC(double temperatureC) {
        this.temperatureC = temperatureC;
        this.lastUpdated = Instant.now();
    }

    /** 습도만 갱신될 때 호출 */
    public void setHumidityPct(double humidityPct) {
        this.humidityPct = humidityPct;
        this.lastUpdated = Instant.now();
    }

    /** 최근 N초 안에 데이터가 들어왔는지로 헬스 체크 */
    public boolean isHealthy(long timeoutSeconds) {
        Instant last = lastUpdated;
        if (last == null) return false; // 한 번도 못 받음 → FAIL

        Instant threshold = Instant.now().minusSeconds(timeoutSeconds);
        return last.isAfter(threshold);
    }
}
