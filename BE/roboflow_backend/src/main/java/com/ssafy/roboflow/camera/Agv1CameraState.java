// src/main/java/com/ssafy/roboflow/camera/Agv1CameraState.java
package com.ssafy.roboflow.camera;

import lombok.Getter;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
@Getter
public class Agv1CameraState {

    private volatile Instant lastSuccess; // 마지막 성공 시각
    private volatile Instant lastFailure; // 마지막 실패 시각

    public synchronized void markSuccess() {
        lastSuccess = Instant.now();
    }

    public synchronized void markFailure() {
        lastFailure = Instant.now();
    }

    /**
     * 최근 N초 안에 성공한 요청이 있고,
     * 그 이후에 실패한 기록이 없으면 "정상"으로 본다.
     */
    public boolean isHealthy(long timeoutSeconds) {
        if (lastSuccess == null) {
            // 한 번도 성공한 적 없음 → 비정상으로 취급(원하면 true로 바꿔도 됨)
            return false;
        }

        Instant now = Instant.now();
        boolean recentSuccess = lastSuccess.isAfter(now.minusSeconds(timeoutSeconds));

        // 최근 실패 시간이 더 최신이면 비정상
        if (lastFailure != null && lastFailure.isAfter(lastSuccess)) {
            return false;
        }

        return recentSuccess;
    }
}
