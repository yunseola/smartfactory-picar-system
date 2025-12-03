# arm_controller.py
import time, sys
sys.path.append("/home/pi1/Adeept_PiCar-Pro/Server")
from RPIservo import ServoCtrl
from servo_config import *

class ArmController:
    def __init__(self, do_reset: bool = True):
        self.sc = ServoCtrl()  # ServoCtrl 객체 생성
        self.sc.start()
        if do_reset:
          self.reset()

    def reset(self):
        # 집게를 먼저 130도로 설정 (moveInit 전에!)
        self.sc.setPWM(SERVO_E, GRIP_OPEN)
        time.sleep(0.3)
        
        # 초기 자세 세팅
        self.sc.initConfig(SERVO_B, B_NEUTRAL, True)
        self.sc.initConfig(SERVO_C, C_NEUTRAL, True)
        self.sc.initConfig(SERVO_D, D_NEUTRAL, True)
        self.sc.moveInit()
        time.sleep(0.5)


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
        """한 번의 집기 동작 (각도는 항상 동일 유지) - 기존 방식"""
        self.sc.setPWM(SERVO_E, GRIP_OPEN)  # 열기
        time.sleep(0.7)
        self.sc.moveAngle(SERVO_C, drop)      # 내려가기
        time.sleep(0.7)
        self.sc.setPWM(SERVO_E, grip_close)   # 닫기
        time.sleep(0.7)

    def grab_once_improved(self, grip_close=GRIP_CLOSE):
        """개선된 집기 동작 - 절대 각도 사용 + 손목 제어 (완전 버전)"""
        # 1. 집게 벌리기
        self.sc.setPWM(SERVO_E, GRIP_OPEN)
        time.sleep(0.5)

        # 2. 손목을 집기 각도로 먼저 설정 (집게가 바닥과 평행)
        self.sc.setPWM(SERVO_D, PICK_D_READY)
        time.sleep(0.3)

        # 3. 팔을 물건 위로 천천히 내리기 (절대 각도)
        self.sc.setPWM(SERVO_C, PICK_C_DOWN)
        time.sleep(0.8)  # 충분한 대기 시간

        # 4. 집게 닫기
        self.sc.setPWM(SERVO_E, grip_close)
        time.sleep(0.8)

        # 5. 들어올리기 (C와 D 동시에)
        self.sc.setPWM(SERVO_C, PICK_C_LIFT)
        self.sc.setPWM(SERVO_D, PICK_D_LIFT)
        time.sleep(0.5)

    def grab_once_improved_lower_only(self, grip_close=GRIP_CLOSE):
        """개선된 집기 동작 - 내리고 잡기만 (들어올리기는 별도)"""
        # 1. 집게 완전히 벌리기 (확실하게, 여러번 명령)
        print(f"[DEBUG] Opening gripper to {GRIP_OPEN} degrees")
        for _ in range(3):  # 3번 반복해서 확실하게 열기
            self.sc.setPWM(SERVO_E, GRIP_OPEN)
            time.sleep(0.3)
        time.sleep(0.5)  # 추가 안정화

        # 2. 손목을 집기 각도로 먼저 설정 (집게가 바닥과 평행)
        self.sc.setPWM(SERVO_D, PICK_D_READY)
        time.sleep(0.5)

        # 3. 팔을 물건 위로 천천히 내리기 (절대 각도)
        print(f"[DEBUG] Lowering arm to {PICK_C_DOWN} degrees")
        self.sc.setPWM(SERVO_C, PICK_C_DOWN)
        time.sleep(1.5)  # 증가: 1.2 -> 1.5 (완전히 내려갈 때까지)

        # 4. 추가 안정화 (완전히 내려간 상태 확인)
        print("[DEBUG] Stabilizing before closing...")
        time.sleep(0.5)

        # 5. 집게를 한 번에 확실하게 닫기 (여러번 명령)
        print(f"[DEBUG] Closing gripper to {grip_close} degrees")
        for _ in range(3):  # 3번 반복해서 확실하게 닫기
            self.sc.setPWM(SERVO_E, grip_close)
            time.sleep(0.5)

        # 6. 집게가 완전히 닫힐 때까지 충분히 대기
        print("[DEBUG] Waiting for gripper to fully close...")
        time.sleep(3.0)  # 집게가 완전히 닫히고 물건을 확실히 잡을 때까지
        print("[DEBUG] Gripper fully closed, ready to lift!")

    def lift(self, lift=UP_C):
        """팔을 들어올리기 - 기존 방식"""
        self.sc.moveAngle(SERVO_C, lift)
        time.sleep(0.35)

    def lift_improved(self):
        """개선된 들어올리기 - 절대 각도 사용"""
        self.sc.setPWM(SERVO_C, PICK_C_LIFT)
        self.sc.setPWM(SERVO_D, PICK_D_LIFT)
        time.sleep(1.0)  # 증가: 0.5 -> 1.0 (물건 들고 안정화)

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
