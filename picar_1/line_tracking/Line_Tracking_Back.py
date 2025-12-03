#!/usr/bin/env python3
# File: Line_Tracking_Backward.py
#
# ✅ 용도: 라인 따라 "후진"만 하는 간단 버전
#   - 센서 논리: 검정(라인)=1, 흰 바탕=0 (원본과 동일)
#   - 기존 파라미터/서보 보정은 그대로 사용
#   - 000(라인 상실) 시에는 일단 정지하고 종료

import time
from gpiozero import Motor, InputDevice
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# ------------------------------------------------------------
# 1) 핀 및 하드웨어 설정 (네 원본과 동일)
# ------------------------------------------------------------

PIN_LINE_L = 19
PIN_LINE_M = 16
PIN_LINE_R = 20

MOTOR_A_EN   = 4
MOTOR_B_EN   = 17
MOTOR_A_IN1  = 26
MOTOR_A_IN2  = 21
MOTOR_B_IN1  = 27
MOTOR_B_IN2  = 18

motor_left  = Motor(forward=MOTOR_B_IN2, backward=MOTOR_B_IN1, enable=MOTOR_B_EN)
motor_right = Motor(forward=MOTOR_A_IN2, backward=MOTOR_A_IN1, enable=MOTOR_A_EN)

# 서보(PCA9685) 설정: 앞바퀴 조향 0번 채널
SERVO_CHANNEL = 0
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50
steer_servo = servo.Servo(
    pca.channels[SERVO_CHANNEL],
    min_pulse=500, max_pulse=2400, actuation_range=180
)

# ------------------------------------------------------------
# 2) 주행/조향 파라미터 (원본과 동일하게 유지)
# ------------------------------------------------------------

CENTER_DEG   = 90
LEFT_MAX     = 150
RIGHT_MAX    = 35
KP           = 34.0
SMOOTH_ALPHA = 0.45

BASE_SPEED   = 0.25
MIN_SPEED    = 0.15
TURN_SLOWDOWN_GAIN = 0.018
LOOP_DT      = 0.05

PWM_SLEW     = 0.05   # 루프당 PWM 변화 최대치
STOP_ON_111  = True   # (선택) 111 패턴에서 멈출지 여부

# ------------------------------------------------------------
# 3) 유틸
# ------------------------------------------------------------

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def read_sensors(sen_left, sen_mid, sen_right):
    L = int(sen_left.value)
    M = int(sen_mid.value)
    R = int(sen_right.value)
    return (L, M, R)

def set_steer_deg(target_deg, prev_deg):
    """서보 조향: 한계클램프 + 스무딩 (원본 방식 그대로)"""
    target_deg = clamp(target_deg, RIGHT_MAX, LEFT_MAX)
    new_deg = SMOOTH_ALPHA * prev_deg + (1.0 - SMOOTH_ALPHA) * target_deg
    steer_servo.angle = new_deg
    return new_deg

def set_drive_backward(pwm):
    pwm = clamp(pwm, 0.0, 1.0)
    motor_left.backward(pwm); motor_right.backward(pwm)

def set_drive_stop():
    motor_left.stop(); motor_right.stop()

# ------------------------------------------------------------
# 4) 메인 루프 (후진 전용)
# ------------------------------------------------------------

def main():
    print("=== Line Tracking BACKWARD Start (black=1, white=0) ===")

    sen_left  = InputDevice(PIN_LINE_L)
    sen_mid   = InputDevice(PIN_LINE_M)
    sen_right = InputDevice(PIN_LINE_R)

    current_deg = CENTER_DEG
    steer_servo.angle = current_deg
    prev_pwm = 0.0

    try:
        while True:
            L, M, R = read_sensors(sen_left, sen_mid, sen_right)

            # 1) 교차/끝점 111 패턴 처리 (원하면 사용)
            if (L, M, R) == (1, 1, 1) and STOP_ON_111:
                set_drive_stop()
                current_deg = set_steer_deg(CENTER_DEG, current_deg)
                print("[111] Cross/End detected → STOP (backward mode)")
                time.sleep(0.3)
                break

            # 2) 라인 상실 (000) → 일단 정지 후 종료
            if (L, M, R) == (0, 0, 0):
                set_drive_stop()
                print("[000] Lost line in backward mode → STOP & EXIT")
                time.sleep(0.3)
                break

            # 3) 에러 계산
            #    전진에서는 error = (R - L)
            #    후진에서는 조향 반응이 반대로 느껴지므로 error = (L - R)로 반전
            error = (L - R)

            target_deg = CENTER_DEG - (KP * error)
            current_deg = set_steer_deg(target_deg, current_deg)

            # 조향 각도에 따른 속도 보정
            steer_dev = abs(current_deg - CENTER_DEG)
            raw_speed = clamp(BASE_SPEED - steer_dev * TURN_SLOWDOWN_GAIN, MIN_SPEED, 1.0)

            # 슬루 제한
            delta = clamp(raw_speed - prev_pwm, -PWM_SLEW, PWM_SLEW)
            speed_cmd = clamp(prev_pwm + delta, 0.0, 1.0)
            prev_pwm = speed_cmd

            # ✅ 후진으로 구동
            set_drive_backward(speed_cmd)

            print(f"[BACK] LMR=({L},{M},{R}) | err={error:+d} | steer={current_deg:5.1f}° → v={speed_cmd:.2f}")

            time.sleep(LOOP_DT)

    except KeyboardInterrupt:
        print("\n[Ctrl+C] Stop")
    finally:
        set_drive_stop()
        steer_servo.angle = CENTER_DEG
        pca.deinit()
        sen_left.close(); sen_mid.close(); sen_right.close()
        print("Clean exit (backward).")

if __name__ == "__main__":
    main()
