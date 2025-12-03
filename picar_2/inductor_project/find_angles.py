# 파일: find_angles.py (짧게 여러 번 실행하며 값만 바꿔보기)
import sys, time
sys.path.append("/home/pi1/Adeept_PiCar-Pro/Server")   # 🔥 경로 추가
from RPIservo import ServoCtrl; import time
SERVO_D, SERVO_E = 3, 4
GRIP_OPEN  = 140   # 바꿔가며 적당한 값 찾기
GRIP_CLOSE = 90   # 바꿔가며 적당한 값 찾기
WRIST_NEUTRAL = 90

sc=ServoCtrl(); sc.start(); sc.moveInit(); time.sleep(1)
sc.setPWM(SERVO_D, WRIST_NEUTRAL)
time.sleep(0.3)
sc.setPWM(SERVO_E, GRIP_OPEN);  time.sleep(0.5)
sc.setPWM(SERVO_E, GRIP_CLOSE); time.sleep(0.5)
