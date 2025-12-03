# 🏭 SmartFactory PiCar System
Raspberry Pi + AI Vision + Robot Arm 기반 인덕터 자동 분류 스마트팩토리 시스템

## 📌 프로젝트 개요
본 프로젝트는 스마트팩토리 환경을 기반으로 제작된 자율 분류 시스템으로,
**Raspberry Pi, AI 비전(YOLOv8), 라인트래킹(IR Sensor), Robot Arm(PCA9685 Servo)** 를 활용하여
컨베이어 위 인덕터를 **실시간 탐지 → 분류 → 픽업 → 이송**하는 End-to-End 자동화 시스템입니다.

YOLO 모델을 통한 실시간 객체 탐지부터
로봇팔 제어, 주행 제어까지 전체 플로우를 직접 설계・구현했습니다.

## 🚀 주요 기능 (Features)
- **YOLOv8 기반 인덕터 실시간 탐지**
- **PiCamera2 영상 스트림 캡처 및 추론 파이프라인 구축**
- **IR Sensor 기반 라인트래킹 주행 제어**
- **PCA9685 기반 4DoF Robot Arm 제어**
- **Pick & Place 자동화 동작 (집기 → 이동 → 배치)**
- AI → 주행 → 로봇팔 제어의 전체 흐름 통합 구현
- 조명/환경 변화를 고려한 영상 전처리 및 추론 안정화

## 🧠 시스템 아키텍처
```
[Camera] → [YOLOv8 Inference] → [Classification]
       ↓
[Line Tracking] → [Motor Control]
       ↓
[Robot Arm Control (PCA9685)]
       ↓
[Pick & Place → Sorting]
```

## 🛠 기술 스택

### Hardware
- Raspberry Pi 4
- PiCamera2
- IR Line Tracking Sensor
- PCA9685 PWM Controller
- 4DoF Servo Robot Arm

### Software & AI
- Python 3
- YOLOv8 (Ultralytics)
- OpenCV
- NumPy
- Picamera2
- gpiozero
- Adafruit PCA9685 Library

## 🎥 시연 자료 (Demo)
(예: docs/demo.gif 또는 구글 드라이브 링크)

## 📚 배운 점
- 다양한 임베디드 환경 변수 고려
- End-to-End 파이프라인 설계 경험
- 비전·주행·로봇팔 제어 통합
- 실제 스마트팩토리 자동화 흐름 구현 경험



## 📄 License
MIT License
