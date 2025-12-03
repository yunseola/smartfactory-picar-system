# camera_vision.py
from ultralytics import YOLO
from picamera2 import Picamera2

class Vision:
    def __init__(self, model_path="best.pt", imgsz=320, conf=0.5, frame_size=(640,480)):
        self.model = YOLO(model_path)
        self.imgsz = imgsz
        self.conf = conf
        self.names = self.model.names
        self.W, self.H = frame_size

        self.picam2 = Picamera2()
        cfg = self.picam2.create_preview_configuration(
            main={"size": (self.W, self.H), "format":"RGB888"}
        )
        self.picam2.configure(cfg)
        try:
            self.picam2.set_controls({"FrameRate":30})
        except:
            pass
        self.picam2.start()

    def get_frame(self):
        return self.picam2.capture_array()

    def detect(self, frame):
        res = self.model.predict(source=frame, imgsz=self.imgsz, conf=self.conf, verbose=False)[0]
        boxes = []
        for box, cls, conf in zip(res.boxes.xyxy, res.boxes.cls, res.boxes.conf):
            x1,y1,x2,y2 = map(int, box.tolist())
            boxes.append((x1,y1,x2,y2,int(cls),float(conf)))
        return boxes

    def stop(self):
        self.picam2.stop()
