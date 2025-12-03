# servo_config.py
# 하드웨어/각도/동작 상수 모음

import sys
# RPIservo.py 경로 등록
sys.path.append("/home/pi1/Adeept_PiCar-Pro/Server")

# ---- 서보 ID 매핑 ----
SERVO_A = 0
SERVO_B = 1  # 좌우(조향)
SERVO_C = 2  # 높이(팔 앞/뒤)
SERVO_D = 3  # 손목 위/아래
SERVO_E = 4  # 집게

# ---- 기준 각도(사용자 세팅) ----
B_NEUTRAL = 90   # 기본 조향
C_NEUTRAL = 130   # 사용자 튠 값
D_NEUTRAL = 90   # 손목

GRIP_OPEN  = 120 # 시작 시 최대로 개방(카메라 안 가림)
GRIP_CLOSE = 45 # 집을 때 각도 (더 세게 잡기: 60 -> 45)

# ---- 좌/중/우 스티어링(1번 서보 각도) ----
# 필요에 따라 아래 값을 조정 (처음엔 ±8~10도 권장)
B_LEFT_ANGLE   = 84   # 왼쪽 물체를 집을 때 B 각도
B_CENTER_ANGLE = 90   # 중앙일 때
B_RIGHT_ANGLE  = 93   # 오른쪽 물체를 집을 때

# ---- 카메라/모델 ----
MODEL_PATH  = "best.pt"
IMGSZ       = 320
CONF        = 0.5
FRAME_SIZE  = (640, 480)
INFER_EVERY = 2

# ---- 동작 파라미터 (기존 방식 - 참고용) ----
DROP_C = 20     # 내려갈 양 (재시도에도 동일)
UP_C   = -8    # 들어올릴 양

# ---- 물건 집기용 절대 각도 (개선된 방식) ----
# test_pick_calibration.py로 최적값을 찾은 후 아래 값을 수정하세요
PICK_C_READY = 1    # 물건 위에 대기할 때 C 각도
PICK_C_DOWN  = 155    # 집게를 내릴 때 C 각도 (바닥 근처, 테스트 후 조정)
PICK_C_LIFT  = 105    # 물건을 들어올렸을 때 C 각도

PICK_D_READY = 120    # 집을 때 손목 각도 (집게가 바닥과 평행, 테스트 후 조정)
PICK_D_LIFT  = 140    # 들어올릴 때 손목 각도

# 연속 감지/정렬 안정화
DETECT_STABLE_FRAMES = 3
POS_STABLE_FRAMES    = 2   # L/C/R 존에 연속 N프레임 자리잡으면 진행

# 좌/중/우 구역(가로 비율)
CENTER_BAND_RATIO = (0.35, 0.65)

# 실패 판정/재시도 (존재/부재 방식)
WAIT_AFTER_LIFT_SEC = 2.0      # 1.5~2.5 권장
VERIFY_MISS_FRAMES  = 4        # (원샷 검증에선 사용 안 해도 있어도 됨)
VERIFY_SEE_FRAMES   = 3        # (동일)
MAX_RETRIES         = 2
LOSE_SIGHT_TIMEOUT  = 1.0

# ==========================================================
# 🔽 여기부터는 "박스에 내려놓기"용 각도 상수
#    (값은 테스트하면서 직접 미세 조정해주면 됨)
# ==========================================================

# 박스가 있는 방향으로 팔을 돌릴 때 B(조향) 절대 각도
# 예: 박스가 오른쪽에 있다면 기본 90에서 +쪽으로 조금 틀어주기
BOX_B_ANGLE = 120   # 예시값. 로봇을 돌려보면서 직접 튜닝

# 박스로 이동할 때 C(높이) 절대 각도
#  - SAFE : 박스 위를 지나갈 때, 어디에도 안 부딪히는 높이
#  - DOWN : 실제 박스 높이(3cm)에 맞춰 살짝 내려간 위치
BOX_C_SAFE = 80     # 예시: 팔이 박스 위를 지날 때 높이 (튜닝)
BOX_C_DOWN = 30     # 예시: 실제로 박스 안에 닿는 높이 (튜닝)

# 박스 위에서 손목(D) 각도(필요 없으면 D_NEUTRAL과 같게 둬도 됨)
BOX_D_ANGLE = 90    # 필요하면 기울이고 싶을 때 조정
