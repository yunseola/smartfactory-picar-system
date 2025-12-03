#!/usr/bin/env python3
"""
라즈베리파이에서 MQTT 트리거를 수신하면 사진을 촬영하고,
HTTP(멀티파트 폼)로 AI 서버에 업로드하는 지속 실행 스크립트.

구성 요소
- Paho MQTT: 브로커와 연결하여 특정 토픽 구독, 메시지 수신 시 콜백 실행
- Picamera2: 라즈베리파이 카메라에서 JPEG 촬영
- requests: 촬영한 이미지를 AI 서버로 전송
- dotenv: .env 환경변수에서 접속 정보/설정을 로드

실행 수명주기
1) Picamera2 초기화 및 워밍업
2) MQTT 브로커 연결 & 토픽 구독
3) 메시지 도착(on_message) → 촬영(capture_to_bytes) → 업로드(upload_to_ai)
4) SIGINT/SIGTERM 수신 시 안전 종료
"""

import os
import io
import json
import signal
import time
import tempfile
from datetime import datetime

from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import requests

from picamera2 import Picamera2

# ---------- 설정 ----------
load_dotenv()  # 같은 디렉토리의 .env 파일을 로드. 없으면 환경변수 그대로 사용.

# MQTT 브로커 접속 정보와 구독할 토픽
MQTT_BROKER_HOST = os.getenv("MQTT_BROKER_HOST", "localhost")
MQTT_BROKER_PORT = int(os.getenv("MQTT_BROKER_PORT", "1883"))
MQTT_TOPIC       = os.getenv("MQTT_TOPIC", "arduino/camera/trigger")
MQTT_USERNAME    = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD    = os.getenv("MQTT_PASSWORD", "")

# 업로드할 AI 서버의 엔드포인트(URL). 멀티파트 폼으로 파일 전송.
AI_POST_URL      = os.getenv("AI_POST_URL", "http://localhost:8000/upload")

# 촬영 해상도 및 JPEG 품질(참고: Picamera2의 품질 적용 방법은 구성/버전에 따라 다를 수 있음)
CAM_WIDTH        = int(os.getenv("CAM_WIDTH", "1920"))
CAM_HEIGHT       = int(os.getenv("CAM_HEIGHT", "1080"))
JPEG_QUALITY     = int(os.getenv("JPEG_QUALITY", "90"))

REQUEST_TIMEOUT  = 10   # HTTP 요청 타임아웃(초)
DEBOUNCE_MS      = 300  # 같은 토픽에서 지나치게 자주 트리거가 올 때 무시하는 최소 간격(밀리초)
# ---------------------------

last_trigger_ts  = 0     # 마지막 트리거 처리 시각(밀리초). 디바운싱 용도.
running = True           # 메인 루프 실행/종료 플래그

# --- Picamera2 초기화 ---
picam = Picamera2()
# 스틸 이미지(정지 화상) 촬영용 구성. main 스트림의 출력 크기를 지정.
# buffer_count는 내부 버퍼 개수. 너무 크면 메모리 사용↑, 너무 작으면 처리 지연↑
cfg = picam.create_still_configuration(
    main={"size": (CAM_WIDTH, CAM_HEIGHT)},
    buffer_count=2
)
picam.configure(cfg)     # 위 구성 적용

picam.options["quality"] = JPEG_QUALITY

picam.set_controls({
        "AfMode": controls.AfModeEnum.Continuous,
        "AfSpeed": controls.AfSpeedEnum.Normal,
})

picam.start()            # 카메라 파이프라인 시작
time.sleep(0.8)          # 센서/AE(자동노출) 안정화 대기 (짧게 0.5~1.0s 권장)

def graceful_shutdown(*_):
    """
    SIGINT(Ctrl+C) 또는 SIGTERM(systemd stop 등) 수신 시
    메인 루프를 빠져나가도록 플래그를 False로 바꾸는 핸들러.
    """
    global running
    running = False

# UNIX 신호 핸들러 등록: 안전 종료를 위해 사용
signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

def capture_to_bytes() -> bytes:
    """
    카메라로 JPEG 1장을 촬영하여 바이트로 반환.
    - 임시 파일에 먼저 저장 후 읽어오는 방식(안정적이며 메모리 사용량 예측 용이)
    - Picamera2는 파일 경로/파일객체/바이트 버퍼 등 다양한 방법을 지원하지만
      임시 파일 방식이 문제 상황에서 디버깅이 쉽고 호환성이 좋아 기본값으로 채택.
    """
    # 임시 파일 생성 (delete=False: Windows 호환 및 이후 수동 삭제를 위해)
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        # JPEG 품질을 제어하려면 Picamera2 버전에 맞는 옵션을 추가 설정해야 함.
        # 예: picam.options['quality'] = JPEG_QUALITY (버전에 따라 지원 여부 상이)
        # 여기서는 기본 캡처 경로만 사용.
        picam.capture_file(tmp_path)  # 실제 촬영/인코딩 수행

        # 바이트로 읽어들여 상위 단계(업로드 함수)로 전달
        with open(tmp_path, "rb") as f:
            data = f.read()
        return data
    finally:
        # 임시 파일 정리(예외 발생 여부와 무관하게 삭제 시도)
        try:
            os.remove(tmp_path)
        except FileNotFoundError:
            pass

def upload_to_ai(image_bytes: bytes, meta: dict):
    """
    촬영한 이미지 바이트를 멀티파트 폼으로 AI 서버에 POST 업로드.
    - files: 실제 바이너리 파일 파트
    - data: 부가 메타데이터(JSON 문자열)
    - 예외 발생 시 raise_for_status로 HTTP 오류를 예외로 전파
    반환값: 서버의 응답 본문(텍스트)
    """
    files = {
        "file": ("capture.jpg", image_bytes, "image/jpeg")
    }
    # 서버에서 메타데이터를 함께 기록/활용할 수 있도록 폼 필드로 전송
    data = {"meta": json.dumps(meta, ensure_ascii=False)}

    # 타임아웃을 지정하여 네트워크 지연/끊김 시 스레드가 영원히 멈추지 않도록 방지
    r = requests.post(AI_POST_URL, files=files, data=data, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()  # 4xx/5xx일 경우 예외 발생
    return r.text

# ---------------- MQTT 콜백 ----------------

def on_connect(client, userdata, flags, rc, properties=None):
    """
    브로커 연결 성공 시 호출.
    - rc(리턴 코드)가 0이면 정상 연결
    - 여기서 구독을 등록해두면 재연결 시에도 자동 호출되어 재구독됨
    """
    print(f"[MQTT] Connected rc={rc}")
    client.subscribe(MQTT_TOPIC, qos=1)  # QoS1: 최소 1회 전달 보장
    print(f"[MQTT] Subscribed: {MQTT_TOPIC}")

def on_message(client, userdata, msg):
    """
    구독한 토픽에 메시지가 도착할 때마다 호출되는 콜백.
    1) 디바운싱(너무 잦은 트리거 무시)
    2) 페이로드 파싱(JSON이면 dict로, 아니면 raw를 메타에 포함)
    3) 촬영 → 업로드 수행, 처리 시간 로그 출력
    4) 예외 발생 시 에러만 로그(서비스는 계속 유지)
    """
    global last_trigger_ts
    now_ms = int(time.time() * 1000)

    # ---- 디바운스: 마지막 처리 이후 DEBOUNCE_MS 미만이면 무시 ----
    if now_ms - last_trigger_ts < DEBOUNCE_MS:
        return
    last_trigger_ts = now_ms

    # 메시지 본문을 UTF-8 문자열로 복구(깨지는 문자는 무시)
    payload = msg.payload.decode("utf-8", errors="ignore").strip()
    print(f"[MQTT] Trigger on {msg.topic}: {payload}")

    # 트리거 메타정보 구성: JSON이면 dict로, 아니면 {"raw": "..."} 형태
    trigger_info = {}
    try:
        trigger_info = json.loads(payload) if payload else {}
    except json.JSONDecodeError:
        trigger_info = {"raw": payload}

    try:
        # ---- 1) 촬영 ----
        t0 = time.time()
        img = capture_to_bytes()
        t1 = time.time()

        # ---- 2) 업로드 ----
        meta = {
            "device": "raspberrypi-4",
            "topic": msg.topic,
            "ts": datetime.utcnow().isoformat() + "Z",  # 업로드 시각(UTC, ISO8601)
            "w": CAM_WIDTH,
            "h": CAM_HEIGHT,
            **trigger_info                     # 트리거에 담긴 부가정보 병합
        }
        resp = upload_to_ai(img, meta)
        t2 = time.time()

        # 처리 시간 로깅(성능 관찰/튜닝에 도움)
        print(f"[OK] Captured in {t1 - t0:.2f}s, uploaded in {t2 - t1:.2f}s, resp={resp[:120]}...")

    except Exception as e:
        # 예외는 로그만 찍고 루프 유지(서비스 지속성 확보)
        print(f"[ERR] {e}")

# ---------------- 메인 엔트리 ----------------

def main():
    """
    애플리케이션 엔트리 포인트.
    - MQTT 클라이언트 생성 및 인증 설정
    - 콜백 등록(on_connect, on_message)
    - 브로커 연결 후 loop_start()로 네트워크 수신 스레드 실행
    - 메인 스레드는 running 플래그가 True인 동안 짧게 sleep 반복(유휴 루프)
    - 종료 시 카메라/네트워크 루프 정리
    """
    client = mqtt.Client()  # 기본 MQTTv3.1.1 클라이언트
    if MQTT_USERNAME:
        # 브로커가 인증을 요구할 때만 설정. 비번이 빈 문자열이면 None 전달
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or None)

    # 콜백 함수 연결
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"[BOOT] Broker={MQTT_BROKER_HOST}:{MQTT_BROKER_PORT}, Topic={MQTT_TOPIC}")

    # keepalive: 브로커와 주기적 핑으로 연결 상태 유지(초)
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)

    # loop_start(): 비동기 네트워크 루프를 백그라운드 스레드로 가동
    try:
        client.loop_start()
        # 메인 스레드는 신호 대기/자원 관리만 수행
        while running:
            time.sleep(0.5)
    finally:
        # 안전 정리: 네트워크 루프 중지 및 카메라 종료
        client.loop_stop()
        picam.stop()
        print("[EXIT] Stopped cleanly.")

# 파이썬 스크립트를 직접 실행했을 때만 main() 호출 (모듈 임포트 시 실행 방지)
if __name__ == "__main__":
    main()
