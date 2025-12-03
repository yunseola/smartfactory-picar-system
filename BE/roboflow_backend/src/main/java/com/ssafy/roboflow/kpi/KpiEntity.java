// src/main/java/com/ssafy/roboflow/kpi/KpiEntity.java
package com.ssafy.roboflow.kpi;

import jakarta.persistence.*;
import lombok.*;

import java.time.Instant;

@Entity
@Table(name = "kpi_totals")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KpiEntity {

    @Id
    private Long id;   // 항상 1만 사용

    @Column(nullable = false)
    private long a0;

    @Column(nullable = false)
    private long a1;

    @Column(nullable = false)
    private long b0;

    @Column(nullable = false)
    private long b1;

    @Column(name = "last_event_ts")
    private Instant lastEventTs; // 마지막 이벤트 시각 (System Status 용)

}
