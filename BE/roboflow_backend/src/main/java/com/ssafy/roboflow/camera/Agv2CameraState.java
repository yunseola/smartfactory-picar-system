// src/main/java/com/ssafy/roboflow/camera/Agv2CameraState.java
package com.ssafy.roboflow.camera;

import lombok.Getter;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
@Getter
public class Agv2CameraState {

    private volatile Instant lastSuccess;
    private volatile Instant lastFailure;

    public synchronized void markSuccess() {
        lastSuccess = Instant.now();
    }

    public synchronized void markFailure() {
        lastFailure = Instant.now();
    }

    public boolean isHealthy(long timeoutSeconds) {
        if (lastSuccess == null) {
            return false; // 한 번도 성공한 적 없으면 비정상으로 취급
        }
        Instant now = Instant.now();
        boolean recentSuccess = lastSuccess.isAfter(now.minusSeconds(timeoutSeconds));

        if (lastFailure != null && lastFailure.isAfter(lastSuccess)) {
            return false;
        }
        return recentSuccess;
    }
}
