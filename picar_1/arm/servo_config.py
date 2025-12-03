# servo_config.py
# 하드웨어/각도/동작 상수 모음

import sys
# RPIservo.py 경로 등록
sys.path.append("/home/pi/adeept_picarpro/Server")

# ---- 서보 ID 매핑 ----
SERVO_A = 0
SERVO_B = 1  # 좌우(조향)
SERVO_C = 2  # 높이(팔 앞/뒤)
SERVO_D = 3  # 손목 위/아래
SERVO_E = 4  # 집게

# ---- 기준 각도(사용자 세팅) ----
B_NEUTRAL = 90   # 기본 조향
C_NEUTRAL = 60   # 사용자 튠 값
D_NEUTRAL = 90   # 손목

GRIP_OPEN  = 180 # 시작 시 최대로 개방(카메라 안 가림)
GRIP_CLOSE =  80 # 집을 때 각도 (재시도에도 항상 동일)

# ---- 좌/중/우 스티어링(1번 서보 각도) ----
# 필요에 따라 아래 값을 조정 (처음엔 ±8~10도 권장)
B_LEFT_ANGLE   = 82   # 왼쪽 물체를 집을 때 B 각도
B_CENTER_ANGLE = 90   # 중앙일 때
B_RIGHT_ANGLE  = 98   # 오른쪽 물체를 집을 때

# ---- 카메라/모델 ----
MODEL_PATH  = "best.pt"
IMGSZ       = 320
CONF        = 0.5
FRAME_SIZE  = (640, 480)
INFER_EVERY = 2

# ---- 동작 파라미터 ----
DROP_C = -5     # 내려갈 양 (재시도에도 동일)
UP_C   = 30    # 들어올릴 양

# 연속 감지/정렬 안정화
DETECT_STABLE_FRAMES = 3
POS_STABLE_FRAMES    = 2   # L/C/R 존에 연속 N프레임 자리잡으면 진행

# 좌/중/우 구역(가로 비율)
CENTER_BAND_RATIO = (0.35, 0.65)

# 실패 판정/재시도 (존재/부재 방식)
VERIFY_MISS_FRAMES = 4   # 연속 N프레임 '안 보이면' 성공 (2~3 추천)
VERIFY_SEE_FRAMES  = 3   # 연속 N프레임 '보이면' 실패
MAX_RETRIES        = 2   # 총 시도: 1+2회
LOSE_SIGHT_TIMEOUT = 3.5 # 집기 중 대상 상실 타임아웃(초)
WAIT_AFTER_LIFT_SEC = 2.0  # 들어올린 뒤 검증까지 기다릴 시간 (1.0 ~ 2.0초)

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
