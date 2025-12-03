#!/usr/bin/env python3
# File: Turn_Return_90.py
#
# 목적:
#   - 이전에 "뒤로 LEFT 90° 회전" 했던 것을
#     "앞으로 LEFT 90° 회전"으로 반대로 되돌려서
#     차의 방향을 원래대로 복귀시키는 전용 스크립트.
#
# 사용:
#   python3 Turn_Return_90.py
#
# 전제:
#   - 핀/서보 파라미터는 Start_Align_180.py와 동일
#   - BACK_SPEED1, BACK_TIME1 도 Start_Align_180.py와 동일해야
#     앞/뒤 회전 각도가 대칭이 되어 방향이 복원됨.

import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo, motor

# ----------------------------------------------------
# 1) 모터/서보 핀 (Server/Move.py 방식)
# ----------------------------------------------------
# PCA9685 모터 채널
MOTOR_M1_IN1 = 15
MOTOR_M1_IN2 = 14
MOTOR_M2_IN1 = 12
MOTOR_M2_IN2 = 13

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

# ----------------------------------------------------
# 2) 조향/속도 파라미터 (움직이면서 회전하도록 조정)
# ----------------------------------------------------
CENTER = 90    # 직진
LEFT   = 50    # 왼쪽 중간 조향 (움직이면서 회전)
RIGHT  = 130   # 오른쪽 중간 조향

# 속도/시간 — 90도 회전용 (후진하면서 회전)
BACK_SPEED = 0.3    # 후진 속도
BACK_TIME  = 2.5    # 후진 시간 (조향이 완만하므로 시간 증가)

# ----------------------------------------------------
# 유틸 함수
# ----------------------------------------------------
def steer(angle):
    steer_servo.angle = angle
    print(f"[STEER] {angle:.1f}°")

def forward(p):
    motor1.throttle = p * M1_Direction
    motor2.throttle = p * M2_Direction
    print(f"[FWD] pwm={p:.2f}")

def backward(p):
    motor1.throttle = -p * M1_Direction
    motor2.throttle = -p * M2_Direction
    print(f"[BACK] pwm={p:.2f}")

def stop():
    motor1.throttle = 0
    motor2.throttle = 0
    print("[STOP]")

# ----------------------------------------------------
# 3) 핵심: 90도 왼쪽 회전 함수 (전진하면서 회전)
# ----------------------------------------------------
def turn_left_90():
    print("=== TURN LEFT 90° (MOVING FORWARD) ===")

    # 0) 초기 정지 & 핸들 중앙
    stop()
    steer(CENTER)
    time.sleep(0.3)

    # 1) 왼쪽 조향 + 후진 (후진하면서 왼쪽으로 90도 회전)
    print("LEFT + BACKWARD (90° turn while moving)")
    steer(LEFT)
    time.sleep(0.2)
    backward(BACK_SPEED)
    time.sleep(BACK_TIME)
    stop()
    time.sleep(0.3)

    # 2) 핸들 중앙으로 복귀
    steer(CENTER)
    time.sleep(0.2)

    print("=== TURN LEFT 90° DONE ===")

# ----------------------------------------------------
# 4) 메인
# ----------------------------------------------------
if __name__ == "__main__":
    try:
        print("⚠ 테스트 전: 바퀴를 공중에 띄우고 동작 확인 권장!")
        time.sleep(1.5)
        turn_left_90()
    except KeyboardInterrupt:
        pass
    finally:
        stop()
        steer(CENTER)
        pca.deinit()
        print("Clean exit.")
