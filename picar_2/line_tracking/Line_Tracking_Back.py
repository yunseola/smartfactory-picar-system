#!/usr/bin/env python3
# File: Line_Tracking_Backward.py
#
# ✅ 용도: 라인 따라 "후진"만 하는 간단 버전
#   - 센서 논리: 검정(라인)=1, 흰 바탕=0 (원본과 동일)
#   - 기존 파라미터/서보 보정은 그대로 사용
#   - 000(라인 상실) 시에는 일단 정지하고 종료

import time
from gpiozero import InputDevice
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo, motor

# ------------------------------------------------------------
# 1) 핀 및 하드웨어 설정 (Server/Move.py 방식)
# ------------------------------------------------------------

PIN_LINE_L = 22
PIN_LINE_M = 27
PIN_LINE_R = 17

# PCA9685 모터 채널 (Server/Move.py와 동일)
MOTOR_M1_IN1 = 15      # M1 정극
MOTOR_M1_IN2 = 14      # M1 부극
MOTOR_M2_IN1 = 12      # M2 정극
MOTOR_M2_IN2 = 13      # M2 부극

M1_Direction = -1
M2_Direction = -1

# I2C 및 PCA9685 설정
i2c = busio.I2C(SCL, SDA)

# PCA9685 (주소 0x5f) - 서보와 모터 모두 같은 보드 사용
pca = PCA9685(i2c, address=0x5f)
pca.frequency = 50

# 서보 설정 (채널 0)
SERVO_CHANNEL = 0
steer_servo = servo.Servo(
    pca.channels[SERVO_CHANNEL],
    min_pulse=500, max_pulse=2400, actuation_range=180
)

# 모터 설정
motor1 = motor.DCMotor(pca.channels[MOTOR_M1_IN1], pca.channels[MOTOR_M1_IN2])
motor1.decay_mode = motor.SLOW_DECAY
motor2 = motor.DCMotor(pca.channels[MOTOR_M2_IN1], pca.channels[MOTOR_M2_IN2])
motor2.decay_mode = motor.SLOW_DECAY

# ------------------------------------------------------------
# 2) 주행/조향 파라미터 (원본과 동일하게 유지)
# ------------------------------------------------------------

CENTER_DEG   = 90
LEFT_MAX     = 92     # 88~92도 사이로만 움직이도록 제한
RIGHT_MAX    = 88     # 88~92도 사이로만 움직이도록 제한
KP           = 34.0
SMOOTH_ALPHA = 0.45

BASE_SPEED   = 0.25
MIN_SPEED    = 0.15
TURN_SLOWDOWN_GAIN = 0.018
LOOP_DT      = 0.05

PWM_SLEW     = 0.05   # 루프당 PWM 변화 최대치
STOP_ON_111  = True   # (선택) 111 패턴에서 멈출지 여부

# 라인 상실 시 복구용 파라미터
CORNER_SPEED = 0.2    # 코너/복구 시 속도
RECOVERY_TIME = 0.15  # 복구 시도 시간

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

def map_speed(speed_0_to_1):
    """0.0~1.0 범위를 -1.0~1.0 throttle로 변환"""
    return speed_0_to_1

def set_drive_forward(pwm):
    """전진: 모터에 양수 throttle 적용"""
    pwm = clamp(pwm, 0.0, 1.0)
    speed = map_speed(pwm)
    # M1_Direction, M2_Direction이 -1이므로 양수 throttle = 전진
    motor1.throttle = speed * M1_Direction
    motor2.throttle = speed * M2_Direction

def set_drive_backward(pwm):
    """후진: M1_Direction, M2_Direction이 -1이므로 부호 반전 필요"""
    pwm = clamp(pwm, 0.0, 1.0)
    speed = map_speed(pwm)
    # Direction이 -1이므로, 후진하려면 양수를 넣되 Direction을 곱하지 않음
    # 또는 Direction 부호를 반대로 적용
    motor1.throttle = speed * (-M1_Direction)  # -1 * -1 = 1 (양수 = 후진)
    motor2.throttle = speed * (-M2_Direction)  # -1 * -1 = 1 (양수 = 후진)

def set_drive_stop():
    motor1.throttle = 0
    motor2.throttle = 0

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

    last_error = 0
    lost_count = 0
    corner_right_frames = 0

    try:
        while True:
            L, M, R = read_sensors(sen_left, sen_mid, sen_right)

            # 1) 라인 상실(000): 전진 코드와 동일한 복원 로직
            if (L, M, R) == (0, 0, 0):
                lost_count += 1
                print(f"[000] Lost line → recovery stage {lost_count}")
                set_drive_stop()

                if last_error > 0:
                    current_deg = set_steer_deg(RIGHT_MAX, current_deg)
                elif last_error < 0:
                    current_deg = set_steer_deg(LEFT_MAX, current_deg)
                else:
                    current_deg = set_steer_deg(CENTER_DEG, current_deg)

                if lost_count <= 3:
                    set_drive_backward(CORNER_SPEED); time.sleep(RECOVERY_TIME)
                elif lost_count <= 6:
                    set_drive_forward(CORNER_SPEED); time.sleep(RECOVERY_TIME)
                else:
                    for tgt in (RIGHT_MAX, LEFT_MAX, RIGHT_MAX):
                        current_deg = set_steer_deg(tgt, current_deg)
                        set_drive_backward(CORNER_SPEED); time.sleep(0.18)

                time.sleep(LOOP_DT)
                continue
            else:
                lost_count = 0

            # 2) 코너 하드턴 모드: (0,0,1) 누적 시 우측 한계 + 초저속 (후진 버전)
            corner_right_frames = corner_right_frames + 1 if (R == 1 and L == 0) else 0
            if corner_right_frames >= 1:
                current_deg = set_steer_deg(RIGHT_MAX, current_deg)
                cmd_pwm = CORNER_SPEED
                delta = clamp(cmd_pwm - prev_pwm, -PWM_SLEW, PWM_SLEW)
                cmd_pwm = clamp(prev_pwm + delta, 0.0, 1.0)
                prev_pwm = cmd_pwm

                set_drive_backward(cmd_pwm)
                if (M == 1) and (R == 0):
                    corner_right_frames = 0
                time.sleep(LOOP_DT)
                continue

            # 3) 일반 주행 (후진)
            # 후진에서는 조향이 반대로 작용하므로 error = (L - R)
            error = (L - R)
            target_deg = CENTER_DEG - (KP * error)
            current_deg = set_steer_deg(target_deg, current_deg)

            steer_dev = abs(current_deg - CENTER_DEG)
            raw_speed = clamp(BASE_SPEED - steer_dev * TURN_SLOWDOWN_GAIN, MIN_SPEED, 1.0)

            # 슬루 제한
            delta = clamp(raw_speed - prev_pwm, -PWM_SLEW, PWM_SLEW)
            speed_cmd = clamp(prev_pwm + delta, 0.0, 1.0)
            prev_pwm = speed_cmd

            # ✅ 후진으로 구동
            set_drive_backward(speed_cmd)

            print(f"[BACK] LMR=({L},{M},{R}) | err={error:+d} | steer={current_deg:5.1f}° → v={speed_cmd:.2f}")
            last_error = error

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
