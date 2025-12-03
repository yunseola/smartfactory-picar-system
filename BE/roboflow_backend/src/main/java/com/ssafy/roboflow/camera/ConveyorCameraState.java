// src/main/java/com/ssafy/roboflow/camera/ConveyorCameraState.java
package com.ssafy.roboflow.camera;

import lombok.Getter;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
@Getter
public class ConveyorCameraState {

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
            return false;
        }
        Instant now = Instant.now();
        boolean recentSuccess = lastSuccess.isAfter(now.minusSeconds(timeoutSeconds));

        if (lastFailure != null && lastFailure.isAfter(lastSuccess)) {
            return false;
        }
        return recentSuccess;
    }
}
