# 파일: find_angles.py (짧게 여러 번 실행하며 값만 바꿔보기)
import sys, time
sys.path.append("/home/pi1/Adeept_PiCar-Pro/Server")   # 🔥 경로 추가
from RPIservo import ServoCtrl; import time

# 서보 채널
SERVO_D = 3  # 손목 (위아래)
SERVO_E = 4  # 집게 (열기/닫기)

# 🔥 여기만 바꿔가며 테스트하기
GRIP_OPEN  = 120   # 집게 열림 각도 (바꿔가며 적당한 값 찾기)
GRIP_CLOSE = 105    # 집게 닫힘 각도 (바꿔가며 적당한 값 찾기)
WRIST_NEUTRAL = 95 # 손목 중립 위치

# 서보 초기화
sc = ServoCtrl()
sc.start()
sc.moveInit()
time.sleep(1)
sc.setPWM(SERVO_D, WRIST_NEUTRAL)
time.sleep(0.3)
sc.setPWM(SERVO_E, GRIP_OPEN); time.sleep(0.5)
sc.setPWM(SERVO_E, GRIP_CLOSE); time.sleep(0.5)

# 손목 중립 위치로
print(f"손목 → {WRIST_NEUTRAL}도")
sc.setPWM(SERVO_D, WRIST_NEUTRAL)
time.sleep(0.3)

# 집게 열기
print(f"집게 열기 → {GRIP_OPEN}도")
sc.setPWM(SERVO_E, GRIP_OPEN)
time.sleep(0.5)

# 집게 닫기
print(f"집게 닫기 → {GRIP_CLOSE}도")
sc.setPWM(SERVO_E, GRIP_CLOSE)
time.sleep(0.5)

print("완료!")
