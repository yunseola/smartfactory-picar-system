// src/main/java/com/ssafy/roboflow/kpi/KpiSummaryDto.java
package com.ssafy.roboflow.kpi;

import lombok.*;

@Getter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class KpiSummaryDto {

    private int total;     // 총 처리량 = 양품 + 불량 전체
    private int lineA;     // 1번 제품(양품만, A0)
    private int lineB;     // 2번 제품(양품만, B0)
    private int defective; // 불량 = A1 + B1
}
