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
from gpiozero import Motor
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# ----------------------------------------------------
# 1) 모터/서보 핀 (Start_Align_180.py와 동일)
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
# 2) 조향/속도 파라미터 (Start_Align_180.py와 동일하게!)
# ----------------------------------------------------
CENTER = 90    # 직진
LEFT   = 175   # 왼쪽 끝
RIGHT  = 5     # 오른쪽 끝 (여기선 안 씀)

# Start_Align_180.py 의 BACK_SPEED1 / BACK_TIME1 과 동일해야 함
BACK_SPEED1 = 0.3
BACK_TIME1  = 1.7

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

def stop():
    motor_left.stop()
    motor_right.stop()
    print("[STOP]")

# ----------------------------------------------------
# 3) 복귀 회전: 앞으로 LEFT 90° 회전
#    (뒤로 LEFT 90°와 반대 회전이 됨)
# ----------------------------------------------------
def turn_return_90():
    print("=== TURN RETURN (FORWARD LEFT 90°) ===")

    # 0) 초기 정지 & 핸들 중앙
    stop()
    steer(CENTER)
    time.sleep(0.4)

    # 1) 왼쪽 최대조향 + 앞으로 전진
    #    → '뒤로 LEFT' 했던 것을 '앞으로 LEFT'로 반대로 되돌리는 동작
    print("STEP 1: LEFT + FWD (return)")
    steer(LEFT)
    time.sleep(0.2)

    forward(BACK_SPEED1)
    time.sleep(BACK_TIME1)

    stop()
    time.sleep(0.3)

    # 2) 핸들 중앙 복귀
    steer(CENTER)
    time.sleep(0.2)

    print("=== RETURN DONE ===")

# ----------------------------------------------------
# 4) 메인
# ----------------------------------------------------
if __name__ == "__main__":
    try:
        print("⚠ 테스트 전: 바퀴를 공중에 띄우고 동작 확인 권장!")
        time.sleep(1.5)
        turn_return_90()
    except KeyboardInterrupt:
        pass
    finally:
        stop()
        steer(CENTER)
        pca.deinit()
        print("Clean exit.")
