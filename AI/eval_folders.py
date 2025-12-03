# eval_folders.py
import os
from pathlib import Path

import torch
from PIL import Image

from app.settings import settings
from app.inference.pipeline import InferencePipeline


# 폴더 구조
# frames_all/
#   ├─ 101_top/
#   ├─ 701_top/
#   └─ defect/
ROOT_DIR = Path("frames_all")

# 폴더 이름 -> 정답 라벨
CLASS_DIRS = {
    "101_top": "101_top",
    "701_top": "701_top",
    "defect": "defect",
}


def main():
    # 모델 로드 (FastAPI에서 쓰는 거 그대로 재사용)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pipe = InferencePipeline(settings.ckpt_path, device)

    labels = ["101_top", "701_top", "defect", "hold"]
    conf = {gt: {pred: 0 for pred in labels} for gt in CLASS_DIRS}

    for folder_name, gt_label in CLASS_DIRS.items():
        folder = ROOT_DIR / folder_name
        if not folder.exists():
            print(f"[WARN] {folder} 없음, 스킵")
            continue

        for fname in os.listdir(folder):
            if not fname.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                continue

            img_path = folder / fname
            img = Image.open(img_path)

            out = pipe.infer_pil(img)  # {"final": "...", "probs": {...}}
            pred = out["final"]

            # 혼동행렬 집계
            if pred not in conf[gt_label]:
                conf[gt_label][pred] = 0
            conf[gt_label][pred] += 1

            # 개별 결과 보고 싶으면 유지, 많으면 주석 처리
            print(f"[{gt_label}] {fname} -> {pred}  probs={out['probs']}")

    print("\n=== Confusion matrix (count) ===")
    for gt_label, row in conf.items():
        print(gt_label, row)


if __name__ == "__main__":
    main()
