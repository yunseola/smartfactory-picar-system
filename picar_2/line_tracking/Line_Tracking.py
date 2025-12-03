# File: Line_Tracking.py
#
# ✅ 센서 논리: 검정(라인)=1, 흰 바탕=0
# ✅ 주요 기능:
#   - 코너 하드턴 모드: (0,0,1) 2프레임 이상 → 우측 한계각 고정 + 초저속
#   - 라인 상실(000) 복원 단계화: 전진→후진→좌우 스윕
#   - 조향 반응 가속(스무딩 완화), 회전 시 속도 자동 감속
#   - 속도 슬루 제한(급발진 방지)

import time
from gpiozero import InputDevice
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo, motor

# ------------------------------------------------------------
# 1) 핀 및 하드웨어 설정 (Server/Move.py 방식)
# ------------------------------------------------------------

# IR 라인트래킹 센서 핀(BCM). (좌/중/우)
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
# 2) 주행/조향 파라미터
# ------------------------------------------------------------

CENTER_DEG   = 90
LEFT_MAX     = 92     # 88~92도 사이로만 움직이도록 제한
RIGHT_MAX    = 88     # 88~92도 사이로만 움직이도록 제한
KP           = 34.0
SMOOTH_ALPHA = 0.45

BASE_SPEED        = 0.25
MIN_SPEED         = 0.15
CORNER_SPEED      = 0.10
TURN_SLOWDOWN_GAIN= 0.018
LOOP_DT           = 0.05

RECOVERY_TIME = 0.25
STOP_ON_111   = True
PWM_SLEW      = 0.05   # 루프당 PWM 변화 최대치

# ------------------------------------------------------------
# 3) 유틸리티
# ------------------------------------------------------------

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def read_sensors(sen_left, sen_mid, sen_right):
    """센서 객체를 인자로 받아 읽기 (전역 의존 제거)"""
    L = int(sen_left.value)
    M = int(sen_mid.value)
    R = int(sen_right.value)
    return (L, M, R)

def set_steer_deg(target_deg, prev_deg):
    """서보 조향: 한계클램프 + 스무딩"""
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
    motor1.throttle = speed * M1_Direction
    motor2.throttle = speed * M2_Direction

def set_drive_backward(pwm):
    """후진: 모터에 음수 throttle 적용"""
    pwm = clamp(pwm, 0.0, 1.0)
    speed = map_speed(pwm)
    motor1.throttle = -speed * M1_Direction
    motor2.throttle = -speed * M2_Direction

def set_drive_stop():
    motor1.throttle = 0
    motor2.throttle = 0

# ------------------------------------------------------------
# 4) 메인 루프
# ------------------------------------------------------------

def main():
    print("=== Line Tracking Start (black=1, white=0) ===")

    # ✅ 센서: 전역이 아니라 여기서만 생성 (중복 점유 방지)
    sen_left  = InputDevice(PIN_LINE_L)
    sen_mid   = InputDevice(PIN_LINE_M)
    sen_right = InputDevice(PIN_LINE_R)

    current_deg = CENTER_DEG
    steer_servo.angle = current_deg
    last_error  = 0

    corner_right_frames = 0
    lost_count = 0
    prev_pwm = 0.0

    try:
        while True:
            L, M, R = read_sensors(sen_left, sen_mid, sen_right)

            # 1) 라인 상실(000): 전진→후진→스윕 단계 복원
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
                    set_drive_forward(CORNER_SPEED);  time.sleep(RECOVERY_TIME)
                elif lost_count <= 6:
                    set_drive_backward(CORNER_SPEED); time.sleep(RECOVERY_TIME)
                else:
                    for tgt in (RIGHT_MAX, LEFT_MAX, RIGHT_MAX):
                        current_deg = set_steer_deg(tgt, current_deg)
                        set_drive_forward(CORNER_SPEED); time.sleep(0.18)

                time.sleep(LOOP_DT)
                continue
            else:
                lost_count = 0

            # 3) 코너 하드턴 모드: (0,0,1) 누적 시 우측 한계 + 초저속
            corner_right_frames = corner_right_frames + 1 if (R == 1 and L == 0) else 0
            if corner_right_frames >= 1:
                current_deg = set_steer_deg(RIGHT_MAX, current_deg)
                cmd_pwm = CORNER_SPEED
                delta = clamp(cmd_pwm - prev_pwm, -PWM_SLEW, PWM_SLEW)
                cmd_pwm = clamp(prev_pwm + delta, 0.0, 1.0)
                prev_pwm = cmd_pwm

                set_drive_forward(cmd_pwm)
                if (M == 1) and (R == 0):  # 중앙이 보이면 해제
                    corner_right_frames = 0
                time.sleep(LOOP_DT)
                continue

            # 4) 일반 주행
            error = (R - L)
            target_deg = CENTER_DEG - (KP * error)
            current_deg = set_steer_deg(target_deg, current_deg)

            steer_dev = abs(current_deg - CENTER_DEG)
            raw_speed = clamp(BASE_SPEED - steer_dev * TURN_SLOWDOWN_GAIN, MIN_SPEED, 1.0)

            # 슬루 제한
            delta = clamp(raw_speed - prev_pwm, -PWM_SLEW, PWM_SLEW)
            speed_cmd = clamp(prev_pwm + delta, 0.0, 1.0)
            prev_pwm = speed_cmd

            set_drive_forward(speed_cmd)
            print(f"LMR=({L},{M},{R}) | err={error:+d} | steer={current_deg:5.1f}° → v={speed_cmd:.2f}")
            last_error = error

            time.sleep(LOOP_DT)

    except KeyboardInterrupt:
        print("\n[Ctrl+C] Stop")
    finally:
        set_drive_stop()
        steer_servo.angle = CENTER_DEG
        pca.deinit()
        # ✅ 센서 핸들 확실히 닫기
        sen_left.close(); sen_mid.close(); sen_right.close()
        print("Clean exit.")

if __name__ == "__main__":
    main()
