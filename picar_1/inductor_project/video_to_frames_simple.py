# 파일명: video_to_frames_simple.py
# 위치: C:\inductor_project\  (이 폴더에 저장하세요)
#
# 기능: 지정한 동영상에서 프레임을 "균등 간격"으로 뽑아서 정확히 200장(가능한 한)에 가깝게 저장합니다.

import cv2
import os
import math

# === 1) 여기만 본인 영상 경로로 확인 ===
VIDEO_PATH = r"C:\Users\SSAFY\Desktop\녹음 2025-11-04 115503.mp4"  # <-- 사용자님 영상 경로

# === 2) 출력 폴더 ===
OUT_DIR = r"C:\inductor_project\frames"

# === 3) 목표 이미지 개수 ===
TARGET_COUNT = 200

# === 4) (선택) 최대 가로 폭 리사이즈 (None이면 원본 유지) ===
MAX_WIDTH = 1280  # 원본 그대로면 None

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        raise RuntimeError(f"동영상을 열 수 없어요:\n{VIDEO_PATH}")

    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        # 일부 코덱은 전체 프레임 수를 못 줄 수 있어서, 그때는 전체를 훑어 세어봅니다.
        # (시간은 조금 더 걸리지만 확실합니다.)
        tmp_count = 0
        while True:
            ok, _ = cap.read()
            if not ok:
                break
            tmp_count += 1
        cap.release()
        total = tmp_count
        cap = cv2.VideoCapture(VIDEO_PATH)

    if total == 0:
        cap.release()
        raise RuntimeError("영상에 프레임이 없는 것 같아요(코덱 문제일 수 있어요).")

    take = min(TARGET_COUNT, total)  # 영상 프레임이 200개보다 적으면 가능한 만큼만
    # 균등 간격 인덱스 만들기 (numpy 없이)
    # 예: total=1600, take=200 → stride=8 → 0, 8, 16, ...
    stride = total / float(take)
    wanted_indices = { int(round(i * stride)) for i in range(take) }
    # 인덱스가 total과 같아지는 걸 방지
    wanted_indices = { idx if idx < total else total - 1 for idx in wanted_indices }

    saved = 0
    current_index = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if current_index in wanted_indices:
            # (선택) 리사이즈
            if MAX_WIDTH is not None and frame.shape[1] > MAX_WIDTH:
                h, w = frame.shape[:2]
                new_w = MAX_WIDTH
                new_h = int(h * (new_w / w))
                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

            out_path = os.path.join(OUT_DIR, f"frame_{saved:04d}.jpg")
            cv2.imwrite(out_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
            saved += 1

            # 다 저장했으면 조기 종료
            if saved >= take:
                break

        current_index += 1

    cap.release()
    print(f"[완료] 총 프레임: {total} | 저장: {saved}장 | 폴더: {OUT_DIR}")

if __name__ == "__main__":
    main()
