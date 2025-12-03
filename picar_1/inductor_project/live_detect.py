# live_detect.py  (Picamera2 + YOLOv8, color-only change: RGB 그대로 표시)
import time
import cv2
from ultralytics import YOLO
from picamera2 import Picamera2

MODEL_PATH = "best.pt"
IMGSZ = 320
CONF  = 0.4
INFER_EVERY = 2

def main():
    cv2.setUseOptimized(True)
    cv2.setNumThreads(2)

    model = YOLO(MODEL_PATH)
    names = model.names

    picam2 = Picamera2()
    # ✅ 색상: 카메라에서 RGB로 받고, 변환 없이 그대로 사용/표시
    config = picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
    picam2.configure(config)
    try:
        picam2.set_controls({"FrameRate": 30})
    except Exception:
        pass
    picam2.start()

    time.sleep(0.1)

    last_boxes = []
    frame_id = 0

    try:
        while True:
            t0 = time.time()

            # ✅ 변환 없이 RGB 그대로 사용
            frame = picam2.capture_array()   # RGB 그대로

            # 격프레임 추론(변경 없음)
            if frame_id % INFER_EVERY == 0:
                results = model.predict(source=frame, imgsz=IMGSZ, conf=CONF, verbose=False)[0]
                last_boxes = []
                for box, cls, conf in zip(results.boxes.xyxy, results.boxes.cls, results.boxes.conf):
                    x1, y1, x2, y2 = map(int, box.tolist())
                    last_boxes.append((x1, y1, x2, y2, int(cls), float(conf)))

            # 박스 그리기(변경 없음) – OpenCV가 BGR 기준이지만, 여기선 색상만 우선
            for x1, y1, x2, y2, cls, conf in last_boxes:
                label = f"{names[cls]} {conf:.2f}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, max(20, y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            fps = 1.0 / max(1e-6, (time.time() - t0))
            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.imshow("Inductor Detection (Picamera2 - RGB raw)", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

            frame_id += 1

    finally:
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
