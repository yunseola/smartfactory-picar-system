// src/main/java/com/ssafy/roboflow/eventlog/EventlogService.java
package com.ssafy.roboflow.eventlog;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import java.time.OffsetDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class EventlogService {

    private final EventlogRepository repository;
    private final SimpMessagingTemplate messagingTemplate;

    // 1) 기존처럼 페이지 조회 (초기 페이지 로딩용)
    public PageResponse<EventLogItemDto> search(
            OffsetDateTime from,
            OffsetDateTime to,
            String module,
            String location,
            int page,
            int size
    ) {
        Specification<EventlogEntity> spec = (root, q, cb) -> cb.conjunction();

        if (from != null) {
            spec = spec.and((root, q, cb) -> cb.greaterThanOrEqualTo(root.get("createdAt"), from));
        }
        if (to != null) {
            spec = spec.and((root, q, cb) -> cb.lessThanOrEqualTo(root.get("createdAt"), to));
        }
        if (module != null && !module.isBlank()) {
            spec = spec.and((root, q, cb) -> cb.equal(root.get("moduleName"), module));
        }
        if (location != null && !location.isBlank()) {
            spec = spec.and((root, q, cb) -> cb.equal(root.get("eventLocation"), location));
        }

        Pageable pageable = PageRequest.of(page, size, Sort.by(Sort.Direction.DESC, "createdAt"));
        Page<EventlogEntity> result = repository.findAll(spec, pageable);

        List<EventLogItemDto> content = result.getContent().stream()
                .map(e -> new EventLogItemDto(
                        e.getCreatedAt(),
                        e.getEventContent(),
                        e.getEventLocation(),
                        e.getProductName(),
                        e.getModuleName()
                ))
                .toList();

        return new PageResponse<>(
                content,
                result.getNumber(),
                result.getSize(),
                result.getTotalElements(),
                result.getTotalPages()
        );
    }

    // 2) 라즈베리파이 / MQTT 쪽에서 들어오는 이벤트를 저장 + 웹으로 push
    public void append(EventLogInputDto input) {
        OffsetDateTime now = OffsetDateTime.now();

        EventlogEntity entity = EventlogEntity.builder()
                .createdAt(now)
                .eventContent(input.getEvent_content())
                .eventLocation(input.getEvent_location())
                .productName(input.getProduct_name())
                .moduleName(input.getModule_name())
                .build();

        repository.save(entity);

        EventLogItemDto dto = new EventLogItemDto(
                entity.getCreatedAt(),
                entity.getEventContent(),
                entity.getEventLocation(),
                entity.getProductName(),
                entity.getModuleName()
        );

        // 구독 경로: /topic/eventlog
        messagingTemplate.convertAndSend("/topic/eventlog", dto);
    }
}
