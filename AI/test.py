# app.py
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import io, os, time, json, datetime

import torch
from torch import nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import timm

# YOLO (ultralytics)
from ultralytics import YOLO

# 외부 통신
import httpx
import paho.mqtt.client as mqtt

# ===================== Config =====================
CKPT_PATH = os.getenv("CKPT_PATH", "runs_mt_v2/inductor_mt_best.pt")  # 멀티태스크 ckpt
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

YOLO_MODEL_PATH = os.getenv("YOLO_MODEL_PATH", "best.pt")
YOLO_CONF_DEFECT = float(os.getenv("YOLO_CONF_DEFECT", "0.5"))

# 결과 전달 대상
SPRING_NOTIFY_URL = os.getenv("SPRING_NOTIFY_URL", "")  # 예: http://<spring-host>:8080/api/infer/result
SPRING_TIMEOUT = float(os.getenv("SPRING_TIMEOUT", "5.0"))

MQTT_BROKER_URL = os.getenv("MQTT_BROKER_URL", "")      # 예: tcp://192.168.0.5:1883
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "factory/inductor/result")
MQTT_QOS = int(os.getenv("MQTT_QOS", "1"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")

# ===================== Multitask Model ======================
class InductorMT(nn.Module):
    """멀티태스크: type(101/701) + defect(불량)"""
    def __init__(self, backbone: str):
        super().__init__()
        self.backbone = timm.create_model(backbone, pretrained=False, num_classes=0, global_pool="avg")
        f = self.backbone.num_features
        self.head_type = nn.Linear(f, 2)    # 101/701
        self.head_def  = nn.Linear(f, 1)    # defect logit

    def forward(self, x):
        h = self.backbone(x)
        return self.head_type(h), self.head_def(h).squeeze(1)

def load_ckpt(path: str):
    try:
        ckpt = torch.load(path, map_location="cpu", weights_only=True)
    except TypeError:
        ckpt = torch.load(path, map_location="cpu")
    return ckpt

ckpt = load_ckpt(CKPT_PATH)
BACKBONE = ckpt.get("backbone", "efficientnet_b2")
IMG_SIZE = int(ckpt.get("img", 384))
BASE_T_DEF = float(ckpt.get("threshold_defect", 0.5))

THRESH_HIGH = float(os.getenv("THRESH_HIGH", BASE_T_DEF))
THRESH_LOW  = float(os.getenv("THRESH_LOW", max(0.0, BASE_T_DEF - 0.02)))

model = InductorMT(BACKBONE)
_ = model.load_state_dict(ckpt["state_dict"], strict=True)
model.to(DEVICE).eval()

# ===================== YOLO Defect Model =====================
yolo_model = YOLO(YOLO_MODEL_PATH)

def yolo_defect_infer_pil(img: Image.Image, conf_th: float = YOLO_CONF_DEFECT) -> Dict:
    results = yolo_model.predict(img, conf=conf_th, verbose=False)
    r = results[0]

    has_defect = False
    num_defects = 0
    max_conf = 0.0

    if r.boxes is not None and len(r.boxes) > 0:
        cls_list = r.boxes.cls.tolist()
        conf_list = r.boxes.conf.tolist()
        for cls_id, c in zip(cls_list, conf_list):
            if int(cls_id) == 1:  # 1 = Scratch_Defect
                num_defects += 1
                if c > max_conf:
                    max_conf = float(c)

    has_defect = num_defects > 0
    return {
        "has_defect": has_defect,
        "num_defects": num_defects,
        "max_conf": max_conf if has_defect else 0.0,
    }

# ===================== Preprocess & TTA =====================
class SquarePad:
    def __call__(self, img: Image.Image):
        w, h = img.size
        if w == h:
            return img
        pad = abs(h - w)
        if w < h:
            return transforms.functional.pad(img, [pad // 2, 0, pad - pad // 2, 0], fill=0)
        else:
            return transforms.functional.pad(img, [0, pad // 2, 0, pad - pad // 2], fill=0)

def build_tf_center(img_size: int):
    return transforms.Compose([
        transforms.Resize(int(img_size * 1.15)),
        transforms.CenterCrop(img_size),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225]),
    ])

def build_tf_square(img_size: int):
    return transforms.Compose([
        SquarePad(),
        transforms.Resize(img_size),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406],
                             [0.229, 0.224, 0.225]),
    ])

TF_LIST = [build_tf_center(IMG_SIZE), build_tf_square(IMG_SIZE)]

@torch.inference_mode()
def infer_pil(img: Image.Image) -> Dict:
    img = img.convert("RGB")
    type_logits_sum = None
    def_logit_sum = 0.0

    for tf in TF_LIST:
        x = tf(img).unsqueeze(0).to(DEVICE, non_blocking=True)
        for flip in (False, True):
            xi = torch.flip(x, dims=[3]) if flip else x
            with torch.cuda.amp.autocast(enabled=(DEVICE.type == "cuda")):
                type_logits, def_logit = model(xi)
            type_logits_sum = type_logits if type_logits_sum is None else (type_logits_sum + type_logits)
            def_logit_sum += def_logit

    n = len(TF_LIST) * 2
    type_logits = type_logits_sum / n
    def_logit = def_logit_sum / n

    p_def = torch.sigmoid(def_logit)[0].item()
    p_type = F.softmax(type_logits, dim=1)[0]

    if p_def >= THRESH_HIGH:
        final = "defect"
    elif p_def >= THRESH_LOW:
        final = "hold"
    else:
        idx = int(torch.argmax(p_type).item())
        final = "101_top" if idx == 0 else "701_top"

    probs = {
        "defect": float(p_def),
        "101_top": float(p_type[0].item()),
        "701_top": float(p_type[1].item()),
    }
    return {"final": final, "probs": probs}

# ===================== 외부 통신 클라이언트 =====================
http_client: Optional[httpx.AsyncClient] = None
mqtt_client: Optional[mqtt.Client] = None

def _parse_mqtt_url(url: str):
    # tcp://host:port 형식만 간단 지원
    if not url.startswith("tcp://"):
        raise ValueError("MQTT_BROKER_URL must start with tcp://")
    host_port = url[len("tcp://"):]
    if ":" in host_port:
        host, port = host_port.split(":", 1)
        return host, int(port)
    return host_port, 1883

async def notify_spring(payload: dict):
    if not SPRING_NOTIFY_URL:
        return
    try:
        assert http_client is not None
        await http_client.post(SPRING_NOTIFY_URL, json=payload, timeout=SPRING_TIMEOUT)
    except Exception:
        # 로깅만 간단 처리 (필요 시 print→logger 교체)
        print("[WARN] notify_spring failed")

def publish_mqtt(payload: dict):
    if mqtt_client is None:
        return
    try:
        msg = json.dumps(payload).encode("utf-8")
        mqtt_client.publish(MQTT_TOPIC, msg, qos=MQTT_QOS)
    except Exception:
        print("[WARN] publish_mqtt failed")

# ===================== FastAPI =====================
app = FastAPI(
    title="Inductor 101/701 + Defect (Multitask + YOLO Defect)",
    version="4.1.0",
    description="라즈베리파이 → FastAPI로 이미지 업로드, 추론 후 스프링/아두이노(MQTT)로 결과 전달",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
async def _startup():
    global http_client, mqtt_client
    try:
        torch.set_num_threads(1)
    except Exception:
        pass
    try:
        with torch.inference_mode():
            x = torch.zeros(1, 3, IMG_SIZE, IMG_SIZE, device=DEVICE)
            _ = model(x)
    except Exception:
        pass

    # httpx 클라이언트
    http_client = httpx.AsyncClient(timeout=SPRING_TIMEOUT)

    # MQTT 클라이언트
    if MQTT_BROKER_URL:
        mqtt_client = mqtt.Client(client_id="fastapi-infer", clean_session=True)
        if MQTT_USERNAME:
            mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD or None)
        host, port = _parse_mqtt_url(MQTT_BROKER_URL)
        try:
            mqtt_client.connect(host, port, keepalive=30)
            mqtt_client.loop_start()
            print(f"[INFO] MQTT connected {host}:{port}, topic={MQTT_TOPIC}")
        except Exception as e:
            print(f"[WARN] MQTT connect failed: {e}")

@app.on_event("shutdown")
async def _shutdown():
    global http_client, mqtt_client
    if http_client is not None:
        await http_client.aclose()
        http_client = None
    if mqtt_client is not None:
        try:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
        except Exception:
            pass
        mqtt_client = None

@app.get("/health")
def health():
    return {
        "status": "ok",
        "device": str(DEVICE),
        "backbone": BACKBONE,
        "img_size": IMG_SIZE,
        "threshold_defect_base": BASE_T_DEF,
        "threshold_high": THRESH_HIGH,
        "threshold_low": THRESH_LOW,
        "ckpt_path": CKPT_PATH,
        "yolo_model_path": YOLO_MODEL_PATH,
        "yolo_conf_defect": YOLO_CONF_DEFECT,
        "tta": {"transforms": ["center", "squarepad"], "flip": True},
        "spring_notify_url": SPRING_NOTIFY_URL,
        "mqtt": {
            "broker_url": MQTT_BROKER_URL,
            "topic": MQTT_TOPIC,
            "qos": MQTT_QOS
        }
    }

class PredictOut(BaseModel):
    final: str
    probs: Dict[str, float]
    latency_ms: float
    yolo_has_defect: bool
    yolo_num_defects: int
    yolo_max_conf: float
    latency_yolo_ms: float

def _build_payload(mt_out: Dict, yolo_out: Dict, latency_all: float, latency_yolo: float, image_id: str) -> dict:
    return {
        "image_id": image_id,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "final": mt_out["final"],
        "probs": mt_out["probs"],
        "latency_ms": round(latency_all, 2),
        "yolo_has_defect": yolo_out["has_defect"],
        "yolo_num_defects": yolo_out["num_defects"],
        "yolo_max_conf": float(yolo_out["max_conf"]),
        "latency_yolo_ms": round(latency_yolo, 2),
    }

@app.post("/predict", response_model=PredictOut)
async def predict(background: BackgroundTasks, file: UploadFile = File(...)):
    b = await file.read()
    img = Image.open(io.BytesIO(b))

    start_all = time.perf_counter()
    mt_out = infer_pil(img)

    start_yolo = time.perf_counter()
    yolo_out = yolo_defect_infer_pil(img)
    latency_yolo = (time.perf_counter() - start_yolo) * 1000
    latency_all = (time.perf_counter() - start_all) * 1000

    image_id = file.filename or "image"
    payload = _build_payload(mt_out, yolo_out, latency_all, latency_yolo, image_id)

    # 응답은 바로 돌려주고, 외부 전송은 백그라운드로
    if SPRING_NOTIFY_URL:
        background.add_task(notify_spring, payload)
    if MQTT_BROKER_URL:
        background.add_task(publish_mqtt, payload)

    return PredictOut(
        final=mt_out["final"],
        probs=mt_out["probs"],
        latency_ms=round(latency_all, 2),
        yolo_has_defect=yolo_out["has_defect"],
        yolo_num_defects=yolo_out["num_defects"],
        yolo_max_conf=float(yolo_out["max_conf"]),
        latency_yolo_ms=round(latency_yolo, 2),
    )

@app.post("/predict_batch", response_model=List[PredictOut])
async def predict_batch(background: BackgroundTasks, files: List[UploadFile] = File(...)):
    results: List[PredictOut] = []
    for f in files:
        b = await f.read()
        img = Image.open(io.BytesIO(b))

        start_all = time.perf_counter()
        mt_out = infer_pil(img)

        start_yolo = time.perf_counter()
        yolo_out = yolo_defect_infer_pil(img)
        latency_yolo = (time.perf_counter() - start_yolo) * 1000
        latency_all = (time.perf_counter() - start_all) * 1000

        image_id = f.filename or "image"
        payload = _build_payload(mt_out, yolo_out, latency_all, latency_yolo, image_id)
        if SPRING_NOTIFY_URL:
            background.add_task(notify_spring, payload)
        if MQTT_BROKER_URL:
            background.add_task(publish_mqtt, payload)

        results.append(PredictOut(
            final=mt_out["final"],
            probs=mt_out["probs"],
            latency_ms=round(latency_all, 2),
            yolo_has_defect=yolo_out["has_defect"],
            yolo_num_defects=yolo_out["num_defects"],
            yolo_max_conf=float(yolo_out["max_conf"]),
            latency_yolo_ms=round(latency_yolo, 2),
        ))
    return results
