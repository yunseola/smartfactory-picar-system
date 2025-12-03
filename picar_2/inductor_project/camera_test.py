# detect_only.py
# Picamera2 + YOLOv8 객체 탐지 화면 테스트 (노란 테두리만)

import cv2
import time
from camera_vision import Vision

# servo_config에 이미 MODEL_PATH, IMGSZ, CONF, FRAME_SIZE가 있다면 이거 쓰고,
# 없으면 아래 주석 풀고 직접 값 넣어줘.
MODEL_PATH = "best.pt"
IMGSZ = 320
CONF = 0.5
FRAME_SIZE = (640, 480)

def main():
    vision = Vision(MODEL_PATH, IMGSZ, CONF, FRAME_SIZE)
    names = vision.names  # 클래스 이름
    W, H = FRAME_SIZE

    print("[INFO] YOLO 탐지 테스트 시작 (ESC 누르면 종료)")

    prev_time = time.time()
    frame_count = 0
    fps = 0.0

    try:
        while True:
            frame = vision.get_frame()
            boxes = vision.detect(frame)

            frame_count += 1
            now = time.time()
            if now - prev_time >= 1.0:
                fps = frame_count / (now - prev_time)
                frame_count = 0
                prev_time = now

            # 박스 그리기
            for (x1, y1, x2, y2, cls, conf) in boxes:
                # 노란색 테두리 (BGR: 0,255,255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                label = f"{names[cls]} {conf:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            # FPS & 안내 문구
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            cv2.putText(frame, "ESC to quit", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            cv2.imshow("YOLO Detect Only (Yellow Box)", frame)

            # ESC 키로 종료
            if cv2.waitKey(1) & 0xFF == 27:
                break

    finally:
        vision.stop()
        cv2.destroyAllWindows()
        print("[INFO] 종료 완료")


if __name__ == "__main__":
    main()
