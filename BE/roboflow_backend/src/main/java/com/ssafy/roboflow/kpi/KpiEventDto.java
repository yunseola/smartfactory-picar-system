// src/main/java/com/ssafy/roboflow/kpi/KpiEventDto.java
package com.ssafy.roboflow.kpi;

import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

@Getter
@Setter
@ToString
public class KpiEventDto {

    // "A0","A1","B0","B1" 중 하나
    private String code;

    // 선택: 밀리초 epoch. 없으면 서버 now 사용
    private Long ts;
}
