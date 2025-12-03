# place_in_box.py
# 이미 물건을 집고 있는 상태에서,
# 박스 높이에 맞춰 팔을 숙이고 물건을 내려놓는 전용 스크립트

import time
from arm_controller import ArmController
from servo_config import BOX_C_DOWN, BOX_C_SAFE, GRIP_OPEN

def main():
    print("[INFO] 박스에 내려놓기 스크립트 시작")

    # 이미 집고 있는 상태이므로 초기화 절대 X
    arm = ArmController(do_reset=False)

    time.sleep(0.2)  # 서보 안정화

    # --- 1) 팔을 박스 높이까지 내리기 ---
    print("[ACTION] 팔을 박스 높이로 내리는 중...")
    arm.sc.setPWM(2, BOX_C_DOWN)    # SERVO_C (팔 높이)
    time.sleep(0.4)

    # --- 2) 집게 열어서 내려놓기 ---
    print("[ACTION] 집게 열기 → 물건 내려놓기")
    arm.sc.setPWM(4, GRIP_OPEN)     # SERVO_E (집게)
    time.sleep(0.4)

    # --- 3) 안전 높이까지 다시 올리기 ---
    print("[ACTION] 팔을 원래 높이로 복귀")
    arm.sc.setPWM(2, BOX_C_SAFE)
    time.sleep(0.4)

    print("[INFO] 박스에 물건을 내려놓았습니다. 종료합니다.")

if __name__ == "__main__":
    main()
