package com.ssafy.roboflow.eventlog;

import lombok.Getter;
import org.springframework.stereotype.Component;

import java.time.Instant;

@Component
@Getter
public class EventlogState {
    // 마지막으로 이벤트를 받은 시간
    private volatile Instant lastReceived = null;

    /** 이벤트 정상 수신 시 호출 */
    public void markReceived() {
        this.lastReceived = Instant.now();
    }

    /** 최근 timeoutSeconds 초 이내에 이벤트를 받았으면 true */
    public boolean isHealthy(long timeoutSeconds) {
        if (lastReceived == null) return false;
        Instant threshold = Instant.now().minusSeconds(timeoutSeconds);
        return lastReceived.isAfter(threshold);
    }
}