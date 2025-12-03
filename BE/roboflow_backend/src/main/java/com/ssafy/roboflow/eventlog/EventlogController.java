// src/main/java/com/ssafy/roboflow/eventlog/EventlogController.java
package com.ssafy.roboflow.eventlog;

import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.messaging.handler.annotation.MessageMapping;
import org.springframework.web.bind.annotation.*;

import java.time.OffsetDateTime;

@RestController
@RequestMapping("/api/eventlog")
@RequiredArgsConstructor
public class EventlogController {

    private final EventlogService service;

    // 1) 초기 Event Log 목록 조회 (기존처럼 REST)
    @GetMapping
    public PageResponse<EventLogItemDto> getEventLogs(
            @RequestParam(value = "from", required = false)
            @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME)
            OffsetDateTime from,

            @RequestParam(value = "to", required = false)
            @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME)
            OffsetDateTime to,

            @RequestParam(value = "module", required = false) String module,
            @RequestParam(value = "location", required = false) String location,

            @RequestParam(value = "page", defaultValue = "0") int page,
            @RequestParam(value = "size", defaultValue = "20") int size
    ) {
        return service.search(from, to, module, location, page, size);
    }

    // 2) (선택) HTTP 로도 새 이벤트 받을 수 있게
    @PostMapping
    public void appendViaHttp(@RequestBody EventLogInputDto input) {
        service.append(input);
    }

    // 3) STOMP 로 들어오는 이벤트 처리: /app/eventlog 로 보내면 여기로 옴
    @MessageMapping("/eventlog")
    public void appendViaStomp(EventLogInputDto input) {
        service.append(input);
    }
}
