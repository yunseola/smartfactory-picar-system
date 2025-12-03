// src/main/java/com/ssafy/roboflow/system/SystemStatusResponse.java
package com.ssafy.roboflow.system;

import lombok.AllArgsConstructor;
import lombok.Getter;

@Getter
@AllArgsConstructor
public class SystemStatusResponse {

    private boolean envOk;      // 환경 상태
    private boolean eventlogOk; // 이벤트 로그 상태
    private boolean kpiOk;      // KPI 상태 추가
    private boolean agv1CamOk;  // AGV1 카메라 상태
    private boolean agv2CamOk;  // AGV2 카메라 상태
    private boolean convCamOk;  // 컨베이어 카메라 상태
}
