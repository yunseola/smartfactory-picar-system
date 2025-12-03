// src/main/java/com/ssafy/roboflow/eventlog/EventlogEntity.java
package com.ssafy.roboflow.eventlog;

import jakarta.persistence.*;
import lombok.*;

import java.time.OffsetDateTime;

@Entity
@Table(name = "event_logs")
@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class EventlogEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "created_at", nullable = false,
            columnDefinition = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    private OffsetDateTime createdAt;

    @Column(name = "event_content", nullable = false, length = 255)
    private String eventContent;

    @Column(name = "event_location", nullable = false, length = 100)
    private String eventLocation;

    @Column(name = "product_name", length = 100)
    private String productName;

    @Column(name = "module_name", nullable = false, length = 100)
    private String moduleName;
}