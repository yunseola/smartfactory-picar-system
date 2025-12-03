// src/main/java/com/ssafy/roboflow/eventlog/EventLogInputDto.java
package com.ssafy.roboflow.eventlog;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;  // @Builder 추가

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder  // @Builder 어노테이션 추가
public class EventLogInputDto {

    private String event_content;
    private String event_location;
    private String product_name;
    private String module_name;
}
