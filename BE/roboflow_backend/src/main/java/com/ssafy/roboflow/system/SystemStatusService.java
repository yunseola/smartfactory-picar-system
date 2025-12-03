// src/main/java/com/ssafy/roboflow/system/SystemStatusService.java
package com.ssafy.roboflow.system;

import com.ssafy.roboflow.camera.Agv1CameraState;
import com.ssafy.roboflow.camera.Agv2CameraState;
import com.ssafy.roboflow.camera.ConveyorCameraState;
import com.ssafy.roboflow.environment.EnvironmentState;
import com.ssafy.roboflow.eventlog.EventlogState;
import com.ssafy.roboflow.kpi.KpiService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class SystemStatusService {

    private final EnvironmentState environmentState;
    private final EventlogState eventlogState;
    private final KpiService kpiService;

    private final Agv1CameraState agv1CameraState;
    private final Agv2CameraState agv2CameraState;
    private final ConveyorCameraState conveyorCameraState;

    public SystemStatusResponse getStatus() {

        // 환경 / 이벤트로그 헬스
        boolean envOk = environmentState.isHealthy(60);   // 최근 60초
        boolean eventlogOk = eventlogState.isHealthy(60);  // 최근 60초

        // KPI: 최근 60초 안에 코드 이벤트가 하나라도 들어왔으면 true
        boolean kpiOk = kpiService.isHealthy(60);

        // 카메라 3대 헬스 (최근 30초 안에 성공한 적 있고, 그 이후 실패가 없으면 true)
        boolean agv1CamOk = agv1CameraState.isHealthy(30);
        boolean agv2CamOk = agv2CameraState.isHealthy(30);
        boolean convCamOk = conveyorCameraState.isHealthy(30);

        // 로그로 상태 값 확인
        System.out.println("envOk: " + envOk);
        System.out.println("eventlogOk: " + eventlogOk);
        System.out.println("kpiOk: " + kpiOk);
        System.out.println("agv1CamOk: " + agv1CamOk);
        System.out.println("agv2CamOk: " + agv2CamOk);
        System.out.println("convCamOk: " + convCamOk);

        return new SystemStatusResponse(
                envOk,
                eventlogOk,
                kpiOk,        // KPI 상태 추가
                agv1CamOk,
                agv2CamOk,
                convCamOk
        );
    }
}
