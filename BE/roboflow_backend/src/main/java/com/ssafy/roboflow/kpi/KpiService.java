// src/main/java/com/ssafy/roboflow/kpi/KpiService.java
package com.ssafy.roboflow.kpi;

import com.ssafy.roboflow.eventlog.EventLogInputDto;
import com.ssafy.roboflow.eventlog.EventlogService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

@Service
@RequiredArgsConstructor
@Slf4j
public class KpiService {

    private static final long KPI_ROW_ID = 1L;

    private final KpiRepository kpiRepository;
    private final SimpMessagingTemplate messagingTemplate;
    private final EventlogService eventlogService;

    /**
     * AI / 임베디드에서 들어오는 코드 한 건 처리
     * code: "A0","A1","B0","B1"
     */
    @Transactional
    public void applyEvent(String code, Instant ts) {
        if (code == null || code.isBlank()) {
            log.warn("[KPI] 빈 코드 수신: {}", code);
            return;
        }

        String normalized = code.trim().toUpperCase();
        if (ts == null) ts = Instant.now();

        // 1) DB에서 KPI 한 줄 로드 (없으면 생성)
        KpiEntity kpi = kpiRepository.findById(KPI_ROW_ID)
                .orElseGet(() -> KpiEntity.builder()
                        .id(KPI_ROW_ID)
                        .a0(0).a1(0).b0(0).b1(0)
                        .lastEventTs(null)
                        .build()
                );

        // 2) 코드에 따라 카운트 +1
        switch (normalized) {
            case "A0" -> kpi.setA0(kpi.getA0() + 1); // 1번 제품 양품
            case "A1" -> kpi.setA1(kpi.getA1() + 1); // 1번 제품 불량
            case "B0" -> kpi.setB0(kpi.getB0() + 1); // 2번 제품 양품
            case "B1" -> kpi.setB1(kpi.getB1() + 1); // 2번 제품 불량
            default -> {
                log.warn("[KPI] 알 수 없는 코드 무시: {}", normalized);
                return;
            }
        }

        kpi.setLastEventTs(ts);
        kpiRepository.save(kpi);

        // 3) KPI 요약 만들어서 STOMP 브로드캐스트
        KpiSummaryDto summary = toSummary(kpi);
        messagingTemplate.convertAndSend("/topic/kpi-summary", summary);
        log.debug("[KPI] summary 브로드캐스트: {}", summary);

        // 4) 불량(A1/B1)만 EventLog에 남기기
        boolean defective = normalized.endsWith("1");
        if (defective) {
            EventLogInputDto logDto = buildDefectEventLog(normalized);
            eventlogService.append(logDto);  // DB 저장 + /topic/eventlog push
            log.info("[KPI] 불량 EventLog 기록: {}", logDto);
        }
    }

    @Transactional(readOnly = true)
    public KpiSummaryDto snapshotSummary() {
        KpiEntity kpi = kpiRepository.findById(KPI_ROW_ID)
                .orElseGet(() -> KpiEntity.builder()
                        .id(KPI_ROW_ID)
                        .a0(0).a1(0).b0(0).b1(0)
                        .lastEventTs(null)
                        .build()
                );
        return toSummary(kpi);
    }

    /**
     * 최근 timeoutSeconds 안에 이벤트가 들어왔는지로 KPI 시스템 상태 체크
     */
    public synchronized boolean isHealthy(long timeoutSeconds) {
        KpiEntity kpi = kpiRepository.findById(KPI_ROW_ID)
                .orElse(null);
        if (kpi == null || kpi.getLastEventTs() == null) {
            return false;
        }

        Instant threshold = Instant.now().minusSeconds(timeoutSeconds);
        return kpi.getLastEventTs().isAfter(threshold);
    }

    // --- 내부 변환 로직들 ---

    /**
     * 요약 규칙:
     *  - lineA: A0 (1번 제품 양품만)
     *  - lineB: B0 (2번 제품 양품만)
     *  - defective: A1 + B1 (전체 불량)
     *  - total: lineA + lineB + defective (전체 처리량)
     */
    private KpiSummaryDto toSummary(KpiEntity k) {
        long goodA = k.getA0();              // 1번 제품(양품)
        long goodB = k.getB0();              // 2번 제품(양품)
        long defective = k.getA1() + k.getB1();
        long total = goodA + goodB + defective;

        return KpiSummaryDto.builder()
                .total((int) total)
                .lineA((int) goodA)
                .lineB((int) goodB)
                .defective((int) defective)
                .build();
    }

    /**
     * A1/B1 불량 이벤트만 EventLog 용 DTO 생성
     */
    private EventLogInputDto buildDefectEventLog(String normalizedCode) {
        String location;
        String productName;

        if (normalizedCode.startsWith("A")) {
            location = "AGV 01";
            productName = "1번 제품";
        } else {
            location = "AGV 02";
            productName = "2번 제품";
        }

        // 여기서는 무조건 불량만 들어온다고 가정 (A1/B1)
        String content = "불량 인덕터 감지";

        return EventLogInputDto.builder()
                .event_content(content)
                .event_location(location)
                .product_name(productName)
                .module_name("KPI")
                .build();
    }
}
