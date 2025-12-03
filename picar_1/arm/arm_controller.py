# arm_controller.py
import time, sys
sys.path.append("/home/pi/adeept_picarpro/Server")
from RPIservo import ServoCtrl
from servo_config import *

class ArmController:
    def __init__(self, do_reset: bool = True):
        self.sc = ServoCtrl()  # ServoCtrl 객체 생성
        self.sc.start()
        if do_reset:
            self.reset()

    def reset(self):
        """초기 자세 세팅 + 집게 오픈"""
        # 초기 자세 세팅
        self.sc.initConfig(SERVO_B, B_NEUTRAL, True)
        self.sc.initConfig(SERVO_C, C_NEUTRAL, True)
        self.sc.initConfig(SERVO_D, D_NEUTRAL, True)
        self.sc.moveInit()
        time.sleep(0.5)
        # 집게 오픈
        self.sc.setPWM(SERVO_E, GRIP_OPEN)

    def steer(self, label: str):
        """좌/중/우 레이블에 맞춰 B 서보 각도 세팅"""
        if label == "LEFT":
            self.sc.setPWM(SERVO_B, B_LEFT_ANGLE)
        elif label == "RIGHT":
            self.sc.setPWM(SERVO_B, B_RIGHT_ANGLE)
        else:
            self.sc.setPWM(SERVO_B, B_CENTER_ANGLE)
        time.sleep(0.1)

    def grab_once(self, drop=DROP_C, grip_close=GRIP_CLOSE):
        """한 번의 집기 동작 (각도는 항상 동일 유지)"""
        # 1) 집게 열기
        self.sc.setPWM(SERVO_E, GRIP_OPEN)
        time.sleep(0.35)

        # 2) 팔 내려가기 (DROP_C는 delta 기준)
        self.sc.moveAngle(SERVO_C, drop)
        time.sleep(0.35)

        # 3) 집게 닫기
        self.sc.setPWM(SERVO_E, grip_close)
        time.sleep(0.35)

    def lift(self, lift=UP_C):
        """팔을 들어올리기 (UP_C는 delta 기준)"""
        self.sc.moveAngle(SERVO_C, lift)
        time.sleep(0.35)

    def recover_soft(self):
        """실패 시 소프트 복구: 열고, C 중립 복귀"""
        self.sc.setPWM(SERVO_E, GRIP_OPEN)
        time.sleep(0.2)
        self.sc.setPWM(SERVO_C, C_NEUTRAL)
        time.sleep(0.2)

    def recover_full(self):
        """최종 실패 시 완전 복귀"""
        self.sc.setPWM(SERVO_E, GRIP_OPEN)
        time.sleep(0.2)
        self.sc.setPWM(SERVO_C, C_NEUTRAL)
        self.sc.setPWM(SERVO_B, B_NEUTRAL)
        time.sleep(0.3)

    # ======================================================
    # 🔽 박스에 내려놓기용 함수들 (새로 추가)
    # ======================================================
    def move_to_box_pose(self):
        """
        이미 물건을 쥐고 있다는 가정 하에,
        팔을 박스 위 '안전한 위치'로 이동시키는 동작
        """
        # 1) C를 안전 높이로
        self.sc.setPWM(SERVO_C, BOX_C_SAFE)
        time.sleep(0.3)

        # 2) B를 박스 방향으로 회전
        self.sc.setPWM(SERVO_B, BOX_B_ANGLE)
        time.sleep(0.3)

        # 3) 손목을 원하는 각도로
        self.sc.setPWM(SERVO_D, BOX_D_ANGLE)
        time.sleep(0.3)

    def place_in_box(self):
        """
        현재 집고 있는 물건을 지정된 박스에 내려놓기.
        - move_to_box_pose()로 박스 위까지 이동
        - BOX_C_DOWN까지 살짝 내려감
        - 집게를 열어 물건을 떨어뜨림
        - 다시 BOX_C_SAFE 높이로 복귀
        """
        # 박스 위로 이동
        self.move_to_box_pose()

        # 박스 높이까지 살짝 내려가기
        self.sc.setPWM(SERVO_C, BOX_C_DOWN)
        time.sleep(0.3)

        # 집게 열어서 내려놓기
        self.sc.setPWM(SERVO_E, GRIP_OPEN)
        time.sleep(0.3)

        # 다시 위로 (안전 높이)
        self.sc.setPWM(SERVO_C, BOX_C_SAFE)
        time.sleep(0.3)
        # 필요하면 여기서 B/D도 원위치로 되돌릴 수 있음
        # self.sc.setPWM(SERVO_B, B_NEUTRAL)
        # self.sc.setPWM(SERVO_D, D_NEUTRAL)
        # time.sleep(0.3)
