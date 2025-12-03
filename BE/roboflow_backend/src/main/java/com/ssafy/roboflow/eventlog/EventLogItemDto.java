// src/main/java/com/ssafy/roboflow/eventlog/EventLogItemDto.java
package com.ssafy.roboflow.eventlog;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.time.OffsetDateTime;

@Getter
@AllArgsConstructor
public class EventLogItemDto {
    private OffsetDateTime created_at;
    private String event_content;
    private String event_location;
    private String product_name;
    private String module_name;
}
