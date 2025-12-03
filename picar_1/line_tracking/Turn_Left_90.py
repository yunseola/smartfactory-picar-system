#!/usr/bin/env python3
# File: Start_Align_180.py
#
# 목적:
#   - 차가 "위쪽"을 보고 시작한다고 가정하고
#   - 아래 라인(콘베이어 반대쪽) 방향을 향하도록 150~180° 회전하는 시동 정렬(A방법)
#
# 동작 순서(강화된 3포인트 턴):
#   1) 왼쪽 최대조향 + 강한 후진 (몸 전체를 크게 틀기)
#   2) 오른쪽 최대조향 + 전진 (너무 틀어진 각도 복구)
#   3) 왼쪽 최대조향 + 짧은 후진 (각도 마무리 → 아래쪽 방향 완성)
#   4) 중앙조향 + 정지

import time
from gpiozero import Motor
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# ----------------------------------------------------
# 1) 모터/서보 핀 (네 라인트래킹 코드와 동일하게)
# ----------------------------------------------------
MOTOR_A_EN   = 4
MOTOR_B_EN   = 17
MOTOR_A_IN1  = 26
MOTOR_A_IN2  = 21
MOTOR_B_IN1  = 27
MOTOR_B_IN2  = 18

motor_left  = Motor(forward=MOTOR_B_IN2, backward=MOTOR_B_IN1, enable=MOTOR_B_EN)
motor_right = Motor(forward=MOTOR_A_IN2, backward=MOTOR_A_IN1, enable=MOTOR_A_EN)

# 서보
SERVO_CHANNEL = 0
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x40)
pca.frequency = 50
steer_servo = servo.Servo(
    pca.channels[SERVO_CHANNEL],
    min_pulse=500, max_pulse=2400, actuation_range=180
)

# ----------------------------------------------------
# 2) 조향/속도 파라미터 (강화)
# ----------------------------------------------------
CENTER = 90    # 직진
LEFT   = 175   # 왼쪽 끝 (조향 극대)
RIGHT  = 5     # 오른쪽 끝

# 속도/시간 — 강하게 강화된 값
BACK_SPEED1 = 0.3   # 첫 강한 후진 속도
BACK_TIME1  = 1.7    # 첫 후진 시간

FWD_SPEED   = 0.3   # 전진 속도
FWD_TIME    = 0.6    # 전진 시간

BACK_SPEED2 = 0.3   # 마지막 후진 속도
BACK_TIME2  = 0.9    # 마지막 후진 시간

# ----------------------------------------------------
# 유틸 함수
# ----------------------------------------------------
def steer(angle):
    steer_servo.angle = angle
    print(f"[STEER] {angle:.1f}°")

def forward(p):
    motor_left.forward(p)
    motor_right.forward(p)
    print(f"[FWD] pwm={p:.2f}")

def backward(p):
    motor_left.backward(p)
    motor_right.backward(p)
    print(f"[BACK] pwm={p:.2f}")

def stop():
    motor_left.stop()
    motor_right.stop()
    print("[STOP]")

# ----------------------------------------------------
# 3) 핵심: 회전(180° 근접) 시동 정렬 함수
# ----------------------------------------------------
def start_align_180():
    print("=== START ALIGN (180° TURN) ===")

    # 0) 초기 정지 & 핸들 중앙
    stop()
    steer(CENTER)
    time.sleep(0.4)

    # 1) 왼쪽 최대조향 + 강한 후진 (가장 많이 돌아가는 단계)
    print("STEP 1: LEFT + BACK (big turn)")
    steer(LEFT)
    time.sleep(0.2)
    backward(BACK_SPEED1)
    time.sleep(BACK_TIME1)
    stop()
    time.sleep(0.3)

    print("=== ALIGN DONE ===")

# ----------------------------------------------------
# 4) 메인
# ----------------------------------------------------
if __name__ == "__main__":
    try:
        print("⚠ 테스트 전: 바퀴를 공중에 띄우고 동작 확인 권장!")
        time.sleep(1.5)
        start_align_180()
    except KeyboardInterrupt:
        pass
    finally:
        stop()
        steer(CENTER)
        pca.deinit()
        print("Clean exit.")
