# app.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import io, os, time

import torch
from torch import nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import timm

# YOLO (ultralytics)
from ultralytics import YOLO

# ===================== Config =====================
CKPT_PATH = os.getenv("CKPT_PATH", "runs_mt_v2/inductor_mt_best.pt")  # 멀티태스크 ckpt
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

YOLO_MODEL_PATH = os.getenv(
    "YOLO_MODEL_PATH",
    "best.pt",
)
YOLO_CONF_DEFECT = float(os.getenv("YOLO_CONF_DEFECT", "0.5"))  # YOLO 결함 판단 conf 임계값 (클래스 1)

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

THRESH_HIGH = float(os.getenv("THRESH_HIGH", BASE_T_DEF))                  # 불량 확정 임계값
THRESH_LOW  = float(os.getenv("THRESH_LOW", max(0.0, BASE_T_DEF - 0.02)))  # 보류 하한

model = InductorMT(BACKBONE)
_ = model.load_state_dict(ckpt["state_dict"], strict=True)
model.to(DEVICE).eval()

# ===================== YOLO Defect Model =====================
yolo_model = YOLO(YOLO_MODEL_PATH)  # 자동으로 GPU 사용

def yolo_defect_infer_pil(img: Image.Image, conf_th: float = YOLO_CONF_DEFECT) -> Dict:
    """
    YOLO로 Scratch_Defect(클래스 1)를 탐지.
    return: {has_defect, num_defects, max_conf}
    """
    # PIL 이미지를 바로 넣어도 됨
    results = yolo_model.predict(
        img,
        conf=conf_th,
        verbose=False
    )
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
    """
    멀티태스크 모델로 101/701 + defect 확률 계산 + 최종 라벨.
    """
    img = img.convert("RGB")
    type_logits_sum = None
    def_logit_sum = 0.0

    # 전처리 2종 × 좌우반전 TTA
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

    # 최종 판정: defect / hold / 101/701
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

# ===================== FastAPI =====================
app = FastAPI(
    title="Inductor 101/701 + Defect (Multitask + YOLO Defect)",
    version="4.0.0",
    description="멀티태스크 분류(101/701+defect) + YOLO 불량 탐지 결과를 동시에 반환하는 API",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.on_event("startup")
def _startup():
    try:
        torch.set_num_threads(1)
    except Exception:
        pass
    # 멀티태스크 모델 워밍업(선택)
    try:
        with torch.inference_mode():
            x = torch.zeros(1, 3, IMG_SIZE, IMG_SIZE, device=DEVICE)
            _ = model(x)
    except Exception:
        pass

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
    }

class PredictOut(BaseModel):
    final: str                      # 멀티태스크 기준 최종 라벨(101/701/defect/hold)
    probs: Dict[str, float]         # 멀티태스크 확률들
    latency_ms: float               # 전체 처리 시간
    yolo_has_defect: bool           # YOLO 기준 결함 존재 여부
    yolo_num_defects: int           # YOLO가 잡은 Scratch_Defect 개수
    yolo_max_conf: float            # YOLO Scratch_Defect 중 최대 conf
    latency_yolo_ms: float          # YOLO 추론 시간(ms)

@app.post("/predict", response_model=PredictOut)
async def predict(file: UploadFile = File(...)):
    b = await file.read()
    img = Image.open(io.BytesIO(b))

    start_all = time.perf_counter()

    # 멀티태스크
    mt_out = infer_pil(img)

    # YOLO 결함 탐지
    start_yolo = time.perf_counter()
    yolo_out = yolo_defect_infer_pil(img)
    latency_yolo = (time.perf_counter() - start_yolo) * 1000

    latency_all = (time.perf_counter() - start_all) * 1000

    return {
        "final": mt_out["final"],
        "probs": mt_out["probs"],
        "latency_ms": round(latency_all, 2),
        "yolo_has_defect": yolo_out["has_defect"],
        "yolo_num_defects": yolo_out["num_defects"],
        "yolo_max_conf": float(yolo_out["max_conf"]),
        "latency_yolo_ms": round(latency_yolo, 2),
    }

@app.post("/predict_batch", response_model=List[PredictOut])
async def predict_batch(files: List[UploadFile] = File(...)):
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

        results.append({
            "final": mt_out["final"],
            "probs": mt_out["probs"],
            "latency_ms": round(latency_all, 2),
            "yolo_has_defect": yolo_out["has_defect"],
            "yolo_num_defects": yolo_out["num_defects"],
            "yolo_max_conf": float(yolo_out["max_conf"]),
            "latency_yolo_ms": round(latency_yolo, 2),
        })
    return results
