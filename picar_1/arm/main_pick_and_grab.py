# ===========================================================
#  main_pick_and_grab.py
#  Picamera2 + YOLOv8 객체 탐지 + Adeept 로봇팔 자동 집기
#  (LIFT 1회만 / 바로 검증 / 한 번 집으면 프로그램 종료)
# ===========================================================

import cv2, time, sys
sys.path.append("/home/pi/adeept_picarpro/Server")
from RPIservo import ServoCtrl
from camera_vision import Vision
from arm_controller import ArmController
from utils_vision import pick_center_target, bbox_center, classify_lr
from servo_config import *

# -----------------------------------------------------------
# ✅ 느린 카메라 대응: 들어올린 후 '원샷' 검증
# -----------------------------------------------------------
def verify_presence_oneshot(vision, shots=5, gap=0.25, min_detects=2, min_box_h=80):
    detects = 0
    for _ in range(shots):
        f = vision.get_frame()
        boxes = vision.detect(f)
        big_count = 0
        for b in boxes:
            x1, y1, x2, y2, cls, conf = b
            h = y2 - y1
            if h >= min_box_h:
                big_count += 1
        if big_count > 0:
            detects += 1
        time.sleep(gap)

    if detects >= min_detects:
        print(f"[DEBUG] 검증결과: 화면에 큰 박스 {detects}회 감지 → 실패")
        return True   # 보인다 → 실패
    else:
        print(f"[DEBUG] 검증결과: 큰 박스 거의 없음({detects}회) → 성공")
        return False  # 안보인다 → 성공


def main():
    vision = Vision(MODEL_PATH, IMGSZ, CONF, FRAME_SIZE)
    arm = ArmController()

    W, H = FRAME_SIZE
    state = "SEARCH"
    seen_stable = 0
    pos_stable = 0
    attempt = 0
    last_seen_time = time.time()
    current_pos_label = "CENTER"
    result_text = ""

    print("[INFO] 시스템 시작: ESC 로 종료")

    # ----------- 초기 집게 벌리기 -----------
    arm.grab_once(drop=DROP_C, grip_close=GRIP_OPEN)  # 집게 벌리기
    time.sleep(1)  # 잠깐 대기 (집게 벌리고 초기화 완료될 때까지)

    try:
        while True:
            frame = vision.get_frame()
            boxes = vision.detect(frame)
            target = pick_center_target(boxes, W, H)
            now = time.time()

            if target:
                last_seen_time = now
                x1, y1, x2, y2, cls, conf = target
                cx, cy = bbox_center(target)
                current_pos_label = classify_lr(cx, W, CENTER_BAND_RATIO)

            # ---------------------------------------------------
            # 상태머신
            # ---------------------------------------------------
            if state == "SEARCH":
                result_text = ""
                if target:
                    seen_stable += 1
                    if seen_stable >= DETECT_STABLE_FRAMES:
                        state = "LOCK"
                        pos_stable = 0
                else:
                    seen_stable = 0

            elif state == "LOCK":
                if not target:
                    state = "SEARCH"
                    seen_stable = 0
                    continue
                pos_stable += 1
                if pos_stable >= POS_STABLE_FRAMES:
                    state = "STEER"

            elif state == "STEER":
                arm.steer("CENTER")
                attempt = 0
                state = "LOWER"

            elif state == "LOWER":
                arm.grab_once(drop=DROP_C, grip_close=GRIP_CLOSE)
                state = "LIFT"

            elif state == "LIFT":
                last_seen_time = time.time()
                arm.lift(lift=UP_C)
                print("[DEBUG] LIFT 완료 → 검증 단계로 이동")

                # ✅ 버퍼 정리 (카메라 지연 방지)
                for _ in range(5):
                    f = vision.get_frame()
                    vision.detect(f)
                    time.sleep(0.25)

                # LIFT 끝나면 즉시 검증으로 이동
                state = "VERIFY"

            elif state == "VERIFY":
                is_seen = verify_presence_oneshot(
                    vision,
                    shots=5,
                    gap=0.25,
                    min_detects=2,
                    min_box_h=80
                )

                if not is_seen:
                    print("[RESULT] ✅ 성공적으로 집음!")
                    result_text = "✅ 성공!"
                    print("[INFO] 프로그램 종료 (한 번만 집기 모드)")
                    vision.stop()
                    cv2.destroyAllWindows()
                    sys.exit(0)

                else:
                    print("[RESULT] ❌ 실패, 복구 중...")
                    result_text = "❌ 실패, 재시도"
                    attempt += 1
                    if attempt > MAX_RETRIES:
                        arm.recover_full()
                        state = "SEARCH"
                        seen_stable = 0
                        pos_stable = 0
                    else:
                        arm.recover_soft()
                        state = "LOCK"
                        pos_stable = 0

            # ---------------------------------------------------
            # 시야 상실 타임아웃 (LIFT 제외)
            # ---------------------------------------------------
            if state in ("LOWER", "VERIFY") and (time.time() - last_seen_time) > LOSE_SIGHT_TIMEOUT:
                arm.recover_soft()
                state = "LOCK"
                pos_stable = 0

            # ---------------------------------------------------
            # 디스플레이 (이 부분을 삭제한 코드)
            # ---------------------------------------------------
            # 디스플레이 관련 코드 제거 (cv2.imshow() / cv2.waitKey() 삭제)

    finally:
        vision.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
