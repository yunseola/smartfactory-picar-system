# File: Line_Tracking.py
#
# ✅ 센서 논리: 검정(라인)=1, 흰 바탕=0
# ✅ 주요 기능:
#   - 코너 하드턴 모드: (0,0,1) 2프레임 이상 → 우측 한계각 고정 + 초저속
#   - 라인 상실(000) 복원 단계화: 전진→후진→좌우 스윕
#   - 조향 반응 가속(스무딩 완화), 회전 시 속도 자동 감속
#   - 속도 슬루 제한(급발진 방지)

import time
from gpiozero import Motor, InputDevice
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

# ------------------------------------------------------------
# 1) 핀 및 하드웨어 설정
# ------------------------------------------------------------

# IR 라인트래킹 센서 핀(BCM). (좌/중/우)
PIN_LINE_L = 19
PIN_LINE_M = 16
PIN_LINE_R = 20

# DC 모터 핀 (뒷바퀴 동일 속도 전/후진)
MOTOR_A_EN   = 4
MOTOR_B_EN   = 17
MOTOR_A_IN1  = 26
MOTOR_A_IN2  = 21
MOTOR_B_IN1  = 27
MOTOR_B_IN2  = 18

# 모터(방향이 뒤집혔다고 해서 forward/backward를 교체하신 버전 유지)
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
# 2) 주행/조향 파라미터
# ------------------------------------------------------------

CENTER_DEG   = 90
LEFT_MAX     = 150
RIGHT_MAX    = 35     # 더 작을수록 우측으로 깊게
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

def set_drive_forward(pwm):
    pwm = clamp(pwm, 0.0, 1.0)
    motor_left.forward(pwm); motor_right.forward(pwm)

def set_drive_backward(pwm):
    pwm = clamp(pwm, 0.0, 1.0)
    motor_left.backward(pwm); motor_right.backward(pwm)

def set_drive_stop():
    motor_left.stop(); motor_right.stop()

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

            # 1) 교차/끝점
            if (L, M, R) == (1, 1, 1):
                if STOP_ON_111:
                    set_drive_stop()
                    current_deg = set_steer_deg(CENTER_DEG, current_deg)
                    print("[111] Cross/End detected → STOP")
                    time.sleep(0.3)
                    continue

            # 2) 라인 상실(000): 전진→후진→스윕 단계 복원
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