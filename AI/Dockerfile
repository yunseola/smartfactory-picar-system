FROM python:3.10-slim

# OpenCV, ultralytics 등에 필요한 시스템 라이브러리
RUN apt-get update && \
    apt-get install -y libgl1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 파이썬 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 + 모델 체크포인트 복사
# 로컬의 app/ 폴더를 컨테이너의 /app/app/ 으로
COPY app ./app

# 모델 파일
COPY inductor_4cls_best.pt .

# (선택) .env도 같이 넣고 싶으면
COPY .env .

# 경로 기준은 WORKDIR=/app 이라서 이렇게 두면 됨
ENV CKPT_PATH=/app/inductor_4cls_best.pt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
