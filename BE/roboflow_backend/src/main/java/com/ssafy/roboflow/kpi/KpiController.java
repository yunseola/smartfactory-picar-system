// src/main/java/com/ssafy/roboflow/kpi/KpiController.java
package com.ssafy.roboflow.kpi;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;

@RestController
@RequestMapping("/api/kpi")
@RequiredArgsConstructor
@Slf4j
public class KpiController {

    private final KpiService service;

    @PostMapping("/event")
    public ResponseEntity<Void> pushEvent(@RequestBody KpiEventDto dto) {
        log.info("[KPI] /api/kpi/event 요청 수신: dto={}", dto);

        if (dto == null || dto.getCode() == null || dto.getCode().isBlank()) {
            log.warn("[KPI] 잘못된 요청: dto={}", dto);
            return ResponseEntity.badRequest().build();
        }

        Instant ts = (dto.getTs() != null)
                ? Instant.ofEpochMilli(dto.getTs())
                : Instant.now();

        service.applyEvent(dto.getCode(), ts);
        return ResponseEntity.ok().build();
    }

    /** 대시보드에서 KPI 요약 조회 */
    @GetMapping("/summary")
    public KpiSummaryDto summary() {
        return service.snapshotSummary();
    }
}
