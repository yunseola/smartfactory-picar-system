// src/main/java/com/ssafy/roboflow/camera/CameraController.java
package com.ssafy.roboflow.camera;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.web.client.RestTemplateBuilder;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.client.RestTemplate;

@RestController
@RequestMapping("/api/cam")
@Slf4j
public class CameraController {

    private final RestTemplate restTemplate;

    private final Agv1CameraState agv1CameraState;
    private final Agv2CameraState agv2CameraState;
    private final ConveyorCameraState conveyorCameraState;

    @Value("${cameras.agv1}")
    private String agv1OfferUrl;

    @Value("${cameras.agv2}")
    private String agv2OfferUrl;

    @Value("${cameras.conveyor}")
    private String conveyorOfferUrl;

    public CameraController(
            RestTemplateBuilder builder,
            Agv1CameraState agv1CameraState,
            Agv2CameraState agv2CameraState,
            ConveyorCameraState conveyorCameraState
    ) {
        this.restTemplate = builder.build();
        this.agv1CameraState = agv1CameraState;
        this.agv2CameraState = agv2CameraState;
        this.conveyorCameraState = conveyorCameraState;
    }

    // ---------- AGV1 ----------

    @PostMapping("/agv1/offer")
    public ResponseEntity<String> proxyAgv1Offer(@RequestBody String body) {
        return proxyOfferCommon(body, agv1OfferUrl, agv1CameraState, "AGV1");
    }

    // ---------- AGV2 ----------

    @PostMapping("/agv2/offer")
    public ResponseEntity<String> proxyAgv2Offer(@RequestBody String body) {
        return proxyOfferCommon(body, agv2OfferUrl, agv2CameraState, "AGV2");
    }

    // ---------- Conveyor ----------

    @PostMapping("/conveyor/offer")
    public ResponseEntity<String> proxyConveyorOffer(@RequestBody String body) {
        return proxyOfferCommon(body, conveyorOfferUrl, conveyorCameraState, "Conveyor");
    }

    // ---------- 공통 로직 ----------

    private ResponseEntity<String> proxyOfferCommon(
            String body,
            String targetUrl,
            Object stateObj,
            String label
    ) {
        CameraHealthState state = wrapState(stateObj);

        try {
            log.info("[{}] offer 전달 시작: url={}, body={}", label, targetUrl, body);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<String> entity = new HttpEntity<>(body, headers);

            ResponseEntity<String> piResponse =
                    restTemplate.postForEntity(targetUrl, entity, String.class);

            log.info("[{}] Pi 응답 status={}, body={}",
                    label, piResponse.getStatusCode(), piResponse.getBody());

            if (piResponse.getStatusCode().is2xxSuccessful()) {
                state.markSuccess();
            } else {
                state.markFailure();
            }

            return ResponseEntity
                    .status(piResponse.getStatusCode())
                    .body(piResponse.getBody());

        } catch (Exception e) {
            log.error("[{}] Pi offer 호출 실패: url={}", label, targetUrl, e);
            state.markFailure();

            return ResponseEntity
                    .status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Pi call error: " + e.getClass().getSimpleName() + " - " + e.getMessage());
        }
    }

    /**
     * 상태 객체의 공통 인터페이스용 래퍼.
     * (Agv1CameraState / Agv2CameraState / ConveyorCameraState 모두 동일 구조라 이렇게 처리)
     */
    private CameraHealthState wrapState(Object delegate) {
        return new CameraHealthState() {
            @Override
            public void markSuccess() {
                if (delegate instanceof Agv1CameraState s) s.markSuccess();
                else if (delegate instanceof Agv2CameraState s) s.markSuccess();
                else if (delegate instanceof ConveyorCameraState s) s.markSuccess();
            }

            @Override
            public void markFailure() {
                if (delegate instanceof Agv1CameraState s) s.markFailure();
                else if (delegate instanceof Agv2CameraState s) s.markFailure();
                else if (delegate instanceof ConveyorCameraState s) s.markFailure();
            }
        };
    }

    private interface CameraHealthState {
        void markSuccess();
        void markFailure();
    }
}
