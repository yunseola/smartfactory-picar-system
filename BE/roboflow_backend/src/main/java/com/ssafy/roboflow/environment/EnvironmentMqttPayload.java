// src/main/java/com/ssafy/roboflow/environment/EnvironmentMqttPayload.java
package com.ssafy.roboflow.environment;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class EnvironmentMqttPayload {
    private Double temperature; // 라즈베리 JSON의 "temperature"
    private Double humidity;    // "humidity"
}
