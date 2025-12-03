#include <AccelStepper.h>
#include <Servo.h>

// ===================== 핀 정의 =====================
// 컨베이어 1 (메인)
#define enable1Pin 8
#define dir1Pin    3
#define step1Pin   2
#define cmd1Pin    23
#define sensor1    22

// 컨베이어 2 (A 인덕터용)
#define enable2Pin 9
#define dir2Pin    5
#define step2Pin   4
#define cmd2Pin    25
#define sensor2    24

// 컨베이어 3 (B 인덕터용)
#define enable3Pin 10
#define dir3Pin    7
#define step3Pin   6
#define cmd3Pin    27
#define sensor3    26

// 분류용 서보
#define servo1Pin 11   // A 분류용
#define servo2Pin 12   // B 분류용

// 스텝모터 인터페이스
#define motorInterfaceType 1

// ===================== 객체 생성 =====================
AccelStepper stepper1(motorInterfaceType, step1Pin, dir1Pin);
AccelStepper stepper2(motorInterfaceType, step2Pin, dir2Pin);
AccelStepper stepper3(motorInterfaceType, step3Pin, dir3Pin);

Servo gateServo1;  // A 게이트
Servo gateServo2;  // B 게이트

// 센서 상태
int state1, state2, state3;

// 서보 각도 설정 (필요에 따라 조정)
#define GATE_CLOSE  0    // 닫힘(직진)
#define GATE_OPEN_A 95   // A 쪽으로 90도
#define GATE_OPEN_B 100  // B 쪽으로 90도

// 컨베이어 동작 상태
bool conveyor1Running = true;
bool conveyor2Running = true;
bool conveyor3Running = true;

// 메인 컨베이어 감지/캡처 상태
bool detectionInProgress = false;   // IR 감지 후 1초 기다리는 중인지
unsigned long detectStartMs = 0;

bool waitingForResult = false;      // AI 결과 대기 중인지

// ===================== 게이트(A/B) 열린 상태 관리 =====================
// A, B 게이트 각각 열린 상태를 개별적으로 관리
bool gateAOpen = false;
bool gateBOpen = false;

unsigned long gateAOpenStartMs = 0;
unsigned long gateBOpenStartMs = 0;

// 각 게이트 유지 시간 (필요하면 다르게 설정 가능)
const unsigned long GATE_A_OPEN_DURATION = 5000; // A 게이트 5초
const unsigned long GATE_B_OPEN_DURATION = 10000; // B 게이트 5초

// ESP32와의 시리얼 버퍼 (Mega의 Serial1 사용)
const uint8_t SERIAL1_BUF_SIZE = 32;
char serial1Buf[SERIAL1_BUF_SIZE];
uint8_t serial1Pos = 0;

//카메라 촬영 타이밍 전역변수
bool conveyorJustStopped = false;   // 정지 직후 상태
unsigned long conveyorStopTime = 0; // 정지된 시각
int prevState1 = HIGH;    // 센서의 이전 상태 저장


// ===================== 함수 선언 =====================
void startConveyor1();
void stopConveyor1();
void startConveyor2();
void stopConveyor2();
void startConveyor3();
void stopConveyor3();

void handleMainConveyorLogic();
void handleSubConveyors();
void handleSerialFromEsp32();
void processEsp32Message(const char* msg);
void onClassificationResult(char type, bool isDefect);
void sendCaptureRequest();

// ===================== setup =====================
void setup() {
  // PC 디버깅용
  Serial.begin(115200);

  // ESP32와 통신용 (Mega TX1=18, RX1=19 사용)
  Serial1.begin(115200);

  // 핀 모드 설정
  pinMode(enable1Pin, OUTPUT);
  pinMode(cmd1Pin, OUTPUT);
  pinMode(sensor1, INPUT_PULLUP);

  pinMode(enable2Pin, OUTPUT);
  pinMode(cmd2Pin, OUTPUT);
  pinMode(sensor2, INPUT_PULLUP);

  pinMode(enable3Pin, OUTPUT);
  pinMode(cmd3Pin, OUTPUT);
  pinMode(sensor3, INPUT_PULLUP);

  // 스텝모터 enable (보통 LOW가 활성인 드라이버 많음)
  digitalWrite(enable1Pin, LOW);
  digitalWrite(enable2Pin, LOW);
  digitalWrite(enable3Pin, LOW);

  // 초기 cmdPin은 HIGH(동작 중)으로 가정
  digitalWrite(cmd1Pin, HIGH);
  digitalWrite(cmd2Pin, HIGH);
  digitalWrite(cmd3Pin, HIGH);

  // 스텝모터 속도 설정 (필요시 조정)
  stepper1.setMaxSpeed(1500);
  stepper1.setSpeed(-1400); // 예: 메인 컨베이어 이동 방향

  stepper2.setMaxSpeed(1000);
  stepper2.setSpeed(900);

  stepper3.setMaxSpeed(1000);
  stepper3.setSpeed(900);

  // 서보 초기화
  gateServo1.attach(servo1Pin);
  gateServo2.attach(servo2Pin);
  gateServo1.write(GATE_CLOSE);
  gateServo2.write(GATE_CLOSE);

  // 컨베이어 초기 동작
  conveyor1Running = true;
  conveyor2Running = true;
  conveyor3Running = true;

  Serial.println("===================================");
  Serial.println("Mega Conveyor Controller Started");
  Serial.println("===================================");
}

// ===================== loop =====================
void loop() {
  // ESP32로부터 오는 AI 분류 결과 처리
  handleSerialFromEsp32();

  // 센서 읽기
  state1 = digitalRead(sensor1);
  state2 = digitalRead(sensor2);
  state3 = digitalRead(sensor3);

  // 메인 컨베이어(1) 로직
  handleMainConveyorLogic();

  // A/B 컨베이어 로직
  handleSubConveyors();

  // ===================== 게이트 열린 시간 관리 =====================
  // A 게이트 타이머 관리
  if (gateAOpen && (millis() - gateAOpenStartMs >= GATE_A_OPEN_DURATION)) {
    gateServo1.write(GATE_CLOSE);   // A 게이트 닫기
    gateAOpen = false;
    Serial.println("[MEGA] Gate A closed after timeout");
  }

  // B 게이트 타이머 관리
  if (gateBOpen && (millis() - gateBOpenStartMs >= GATE_B_OPEN_DURATION)) {
    gateServo2.write(GATE_CLOSE);   // B 게이트 닫기
    gateBOpen = false;
    Serial.println("[MEGA] Gate B closed after timeout");
  }

  // 실제 스텝모터 구동
  if (conveyor1Running) stepper1.runSpeed();
  if (conveyor2Running) stepper2.runSpeed();
  if (conveyor3Running) stepper3.runSpeed();
}

// ===================== 메인 컨베이어 로직 =====================
void handleMainConveyorLogic() {
  // 이미 결과 대기 중이면 새 감지 무시
  if (waitingForResult) {
    prevState1 = state1; // 다음 루프를 위한 상태 저장
    return;
  }

  // 1) 감지 시작: HIGH → LOW 전이일 때만 감지 시작
  if (!detectionInProgress &&
      !conveyorJustStopped &&
      prevState1 == HIGH && state1 == LOW) {

    detectionInProgress = true;
    detectStartMs = millis();
    Serial.println("[MEGA] Object detected (HIGH->LOW) → waiting 0.5s before STOP");
  }

  // 2) 감지 후 0.5초 뒤 → 메인 컨베이어 STOP
  if (detectionInProgress &&
      (millis() - detectStartMs >= 600) &&
      conveyor1Running) {

    Serial.println("[MEGA] 0.5s passed → STOP main conveyor");
    stopConveyor1();

    conveyorJustStopped = true;
    conveyorStopTime = millis();

    detectionInProgress = false;  // 감지 대기 종료
  }

  // 3) STOP 후 0.5초 지나면 CAPTURE 요청
  if (conveyorJustStopped &&
      (millis() - conveyorStopTime >= 1000)) {

    Serial.println("[MEGA] 0.5s after STOP → send CAPTURE");
    sendCaptureRequest();

    waitingForResult = true;
    conveyorJustStopped = false;
  }

  // 4) 마지막에 이전 상태 업데이트
  prevState1 = state1;
}



// ===================== A/B 서브 컨베이어 로직 =====================
void handleSubConveyors() {
  // A 인덕터용 컨베이어 (2)
  // 센서 앞에 인덕터가 있으면 멈춤, 사라지면 다시 동작
  if (state2 == LOW) {
    stopConveyor2();
  } else {
    startConveyor2();
  }

  // B 인덕터용 컨베이어 (3)
  if (state3 == LOW) {
    stopConveyor3();
  } else {
    startConveyor3();
  }
}

// ===================== ESP32 시리얼 통신 =====================
void handleSerialFromEsp32() {
  while (Serial1.available() > 0) {
    char c = Serial1.read();

    if (c == '\n' || c == '\r') {
      if (serial1Pos > 0) {
        serial1Buf[serial1Pos] = '\0';
        processEsp32Message(serial1Buf);
        serial1Pos = 0;
      }
    } else {
      if (serial1Pos < SERIAL1_BUF_SIZE - 1) {
        serial1Buf[serial1Pos++] = c;
      }
    }
  }
}

// ESP32로부터 오는 메시지 처리
// 형식 예: "A0" 또는 "B1"  (타입,손상여부(0:정상,1:불량))
void processEsp32Message(const char* msg) {
  Serial.print("[MEGA] From ESP32: ");
  Serial.println(msg);

  if (strlen(msg) < 2) return;

  char type = msg[0];
  int defectInt = msg[1] - '0';
  bool isDefect = (defectInt == 1);

  onClassificationResult(type, isDefect);
}

// ===================== AI 서버 분류 결과에 따라 동작 =====================
void onClassificationResult(char type, bool isDefect) {
  waitingForResult = false;  // 결과 받았으므로 다음 감지 가능

  if (isDefect) {
    // 불량품: 게이트는 둘 다 닫고, 메인 컨베이어는 다시 돌려서 끝으로 떨어지게
    Serial.println("[MEGA] Result: DEFECT → gates closed, main conveyor resumes (drop at end)");
    gateServo1.write(GATE_CLOSE);
    gateServo2.write(GATE_CLOSE);

    // A/B 타이머 플래그 리셋
    gateAOpen = false;
    gateBOpen = false;

    startConveyor1();
    return;
  }

  // 양품: 타입에 따라 분류
  if (type == 'A' || type == 'a') {
    Serial.println("[MEGA] Result: GOOD, TYPE A → open gate A");
    gateServo1.write(GATE_OPEN_A);
    gateServo2.write(GATE_CLOSE);

    // A 게이트 타이머 시작
    gateAOpen = true;
    gateAOpenStartMs = millis();
    gateBOpen = false; // 혹시 B가 열려있었다면 논리적으로는 닫힌 상태 유지

  } else if (type == 'B' || type == 'b') {
    Serial.println("[MEGA] Result: GOOD, TYPE B → open gate B");
    gateServo1.write(GATE_CLOSE);
    gateServo2.write(GATE_OPEN_B);

    // B 게이트 타이머 시작
    gateBOpen = true;
    gateBOpenStartMs = millis();
    gateAOpen = false; // 혹시 A가 열려있었다면 논리적으로는 닫힌 상태 유지

  } else {
    // 알 수 없는 타입이면 안전하게 둘 다 닫고 그냥 통과
    Serial.println("[MEGA] Result: UNKNOWN TYPE → close all gates");
    gateServo1.write(GATE_CLOSE);
    gateServo2.write(GATE_CLOSE);
    gateAOpen = false;
    gateBOpen = false;
  }

  // 메인 컨베이어 다시 동작 (물건을 A/B 쪽으로 떨어뜨리기)
  startConveyor1();
}

// ===================== CAPTURE 요청 =====================
void sendCaptureRequest() {
  Serial1.println("CAPTURE");
  Serial.println("[MEGA] Sent CAPTURE to ESP32");
}

// ===================== 컨베이어 start/stop 함수 =====================
void startConveyor1() {
  if (!conveyor1Running) {
    digitalWrite(cmd1Pin, HIGH);
    stepper1.setSpeed(-1300);
    conveyor1Running = true;
    Serial.println("[MEGA] Main conveyor START");
  }
}

void stopConveyor1() {
  if (conveyor1Running) {
    digitalWrite(cmd1Pin, LOW);
    stepper1.setSpeed(0);
    conveyor1Running = false;
    Serial.println("[MEGA] Main conveyor STOP");
  }
}

void startConveyor2() {
  if (!conveyor2Running) {
    digitalWrite(cmd2Pin, HIGH);
    stepper2.setSpeed(900);
    conveyor2Running = true;
    Serial.println("[MEGA] A conveyor START");
  }
}

void stopConveyor2() {
  if (conveyor2Running) {
    digitalWrite(cmd2Pin, LOW);
    stepper2.setSpeed(0);
    conveyor2Running = false;
    Serial.println("[MEGA] A conveyor STOP");
  }
}

void startConveyor3() {
  if (!conveyor3Running) {
    digitalWrite(cmd3Pin, HIGH);
    stepper3.setSpeed(900);
    conveyor3Running = true;
    Serial.println("[MEGA] B conveyor START");
  }
}

void stopConveyor3() {
  if (conveyor3Running) {
    digitalWrite(cmd3Pin, LOW);
    stepper3.setSpeed(0);
    conveyor3Running = false;
    Serial.println("[MEGA] B conveyor STOP");
  }
}
