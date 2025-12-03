#!/usr/bin/env python3
# File: scenario_line_box.py
#
# 시나리오 순서:
#   1) 라인트래킹으로 후진 (Line_Tracking_Backward.py)
#   2) 왼쪽 90도 회전 (네가 원래 쓰던 회전 스크립트)
#   3) 박스에 물건 내려놓기 (place_in_box.py)
#   4) 오른쪽 90도 회전 (네가 원래 쓰던 회전 스크립트)
#   5) 라인트래킹으로 전진 (Line_Tracking.py)
#
# ✅ 중요한 포인트
#   - 이 스크립트는 모터/서보/센서를 직접 만지지 않고,
#     이미 잘 동작하는 개별 스크립트들을 "순서대로 실행"만 해준다.
#   - 각 스텝은 별도 프로세스로 돌아가서 서로 간섭이 최소화된다.

import time
import subprocess

# ----------------------------------------------------
# 1) 각 기능 스크립트 경로 (네 환경에 맞게 확인만 하면 됨)
# ----------------------------------------------------

# 후진 라인트래킹 (지금 잘 되는 파일)
BACKWARD_LINE_PATH = "/home/pi/adeept_picarpro/Examples/06_Line_Tracking/Line_Tracking_Back.py"

# 전진 라인트래킹 (원본)
FORWARD_LINE_PATH  = "/home/pi/adeept_picarpro/Examples/06_Line_Tracking/Line_Tracking.py"

# 왼쪽 회전 스크립트 (네가 실제 사용하는 왼쪽 90도 회전 코드로 설정)
TURN_LEFT_90_PATH  = "/home/pi/adeept_picarpro/Examples/06_Line_Tracking/Turn_Left_90.py"

# 복구 회전 스크립트 (실제 사용하는 파일 경로로 수정해서 쓰면 됨)
TURN_RIGHT_90_PATH = "/home/pi/adeept_picarpro/Examples/06_Line_Tracking/Turn_Return_90.py"

# 박스에 물건 내려놓기
PLACE_IN_BOX_PATH  = "/home/pi/inductor_project/place_in_box.py"

# ----------------------------------------------------
# 2) 유틸 함수: 다른 파이썬 스크립트 실행
# ----------------------------------------------------

def run_script(path, timeout=None):
    """
    다른 파이썬 스크립트를 별도 프로세스로 실행.
    - timeout=None  : 끝날 때까지 기다림 (라인트래킹 제외 대부분)
    - timeout=초    : 일정 시간 후 종료 (예: 후진/전진 라인트래킹)
    """
    print(f"\n[RUN] {path} (timeout={timeout})")

    # python3로 해당 스크립트 실행
    proc = subprocess.Popen(["python3", path])

    if timeout is None:
        # 스크립트가 자체적으로 종료될 때까지 기다림
        proc.wait()
        print(f"[END] {path} (정상 종료)")
    else:
        # 일정 시간만 돌리고 자동으로 종료
        try:
            proc.wait(timeout=timeout)
            print(f"[END] {path} (timeout 이전에 정상 종료)")
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] {path} → terminate 시도")
            proc.terminate()
            try:
                proc.wait(timeout=1.0)
                print(f"[END] {path} (terminate 성공)")
            except subprocess.TimeoutExpired:
                print(f"[KILL] {path} 강제 종료")
                proc.kill()

# ----------------------------------------------------
# 3) 메인 시나리오
# ----------------------------------------------------

def main():
    print("⚠ 테스트 전에는 바퀴를 공중에 띄워서 먼저 동작 확인하세요!")
    time.sleep(1.5)

    print("=== Scenario: line back → left 90 → box → right 90 → line forward ===")

    # STEP 1) 라인트래킹으로 후진
    #   - Line_Tracking_Backward.py는 무한루프일 가능성이 크니까
    #     timeout으로 "얼마나 오래 후진할지"를 정해준다.
    print("\n[STEP 1] 라인트래킹 후진 시작")
    # 예: 1.5초 동안 후진. 필요하면 1.0 ~ 2.0 사이에서 튜닝.
    run_script(BACKWARD_LINE_PATH, timeout=1.5)
    print("[STEP 1] 라인트래킹 후진 종료")

    # STEP 2) 왼쪽 90도 회전
    print("\n[STEP 2] 왼쪽 90도 회전")
    run_script(TURN_LEFT_90_PATH)   # 이 스크립트 안에서 알아서 끝나야 함
    print("[STEP 2] 왼쪽 회전 종료")

    # STEP 3) 박스에 물건 내려놓기
    print("\n[STEP 3] 박스에 물건 내려놓기")
    run_script(PLACE_IN_BOX_PATH)   # place_in_box.py 원본 그대로 사용
    print("[STEP 3] 박스 작업 종료")

    # STEP 4) 오른쪽 90도 회전 (원래 각도로 복귀)
    print("\n[STEP 4] 오른쪽 90도 회전")
    run_script(TURN_RIGHT_90_PATH)
    print("[STEP 4] 오른쪽 회전 종료")

    # STEP 5) 라인트래킹으로 전진
    print("\n[STEP 5] 라인트래킹 전진 시작")
    # (1) 일정 시간만 전진시키고 자동 종료하고 싶으면 timeout에 값 넣기
    # run_script(FORWARD_LINE_PATH, timeout=3.0)

    # (2) 계속 전진시키고, 사람이 Ctrl+C로 끄고 싶으면 timeout=None
    run_script(FORWARD_LINE_PATH, timeout=None)

    print("\n=== Scenario ALL DONE ===")

# ----------------------------------------------------
# 4) 실행부
# ----------------------------------------------------

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[Ctrl+C] 시나리오 강제 종료")
