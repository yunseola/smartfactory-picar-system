#include <AccelStepper.h>
#include <Servo.h>

// ========== 컨베이어 벨트 1 (메인) ==========
#define enable1Pin 8
#define dir1Pin 3
#define step1Pin 2
#define cmd1Pin 23
#define sensor1 22

// ========== 컨베이어 벨트 2 (경로1) ==========
#define enable2Pin 9
#define dir2Pin 5
#define step2Pin 4
#define cmd2Pin 25
#define sensor2 24

// ========== 컨베이어 벨트 3 (경로2) ==========
#define enable3Pin 10
#define dir3Pin 7
#define step3Pin 6
#define cmd3Pin 27
#define sensor3 26

// ========== 서보모터 (가림막) ==========
#define servo1Pin 11  // 경로1 분기 가림막
#define servo2Pin 12  // 경로2 분기 가림막

#define motorInterfaceType 1

// AccelStepper 객체 생성
AccelStepper stepper1 = AccelStepper(motorInterfaceType, step1Pin, dir1Pin);
AccelStepper stepper2 = AccelStepper(motorInterfaceType, step2Pin, dir2Pin);
AccelStepper stepper3 = AccelStepper(motorInterfaceType, step3Pin, dir3Pin);

// 서보모터 객체 생성
Servo gateServo1;  // 경로1 가림막
Servo gateServo2;  // 경로2 가림막

// 센서 상태 변수
int state1, state2, state3;

// 서보 각도 설정 (MG996R용)
#define GATE_CLOSE 0      // 가림막 닫힘 (직진)
#define GATE_OPEN_1 90    // 경로1로 분기
#define GATE_OPEN_2 90    // 경로2로 분기

void setup() {
  Serial.begin(115200);
  
  // ========== 컨베이어 1 설정 ==========
  pinMode(enable1Pin, OUTPUT);
  pinMode(sensor1, INPUT_PULLUP);
  pinMode(cmd1Pin, OUTPUT);
  
  digitalWrite(enable1Pin, LOW);
  digitalWrite(cmd1Pin, HIGH);
  digitalWrite(sensor1, HIGH);
  
  stepper1.setMaxSpeed(1500);
  stepper1.setSpeed(-1300);
  
  // ========== 컨베이어 2 설정 ==========
  pinMode(enable2Pin, OUTPUT);
  pinMode(sensor2, INPUT_PULLUP);
  pinMode(cmd2Pin, OUTPUT);
  
  digitalWrite(enable2Pin, LOW);
  digitalWrite(cmd2Pin, HIGH);
  digitalWrite(sensor2, HIGH);
  
  stepper2.setMaxSpeed(1000);
  stepper2.setSpeed(900);
  
  // ========== 컨베이어 3 설정 ==========
  pinMode(enable3Pin, OUTPUT);
  pinMode(sensor3, INPUT_PULLUP);
  pinMode(cmd3Pin, OUTPUT);
  
  digitalWrite(enable3Pin, LOW);
  digitalWrite(cmd3Pin, HIGH);
  digitalWrite(sensor3, HIGH);
  
  stepper3.setMaxSpeed(1000);
  stepper3.setSpeed(900);
  
  // ========== 서보모터 설정 ==========
  gateServo1.attach(servo1Pin);
  gateServo2.attach(servo2Pin);
  
  // 초기 위치: 가림막 닫힘 (직진)
  gateServo1.write(GATE_CLOSE);
  gateServo2.write(GATE_CLOSE);
  
  Serial.println("===================================");
  Serial.println("3 Conveyors + 2 Servo Gates Ready");
  Serial.println("===================================");
  Serial.println("Commands:");
  Serial.println("  1 - Close all gates (straight)");
  Serial.println("  2 - Open gate 1 (route 1)");
  Serial.println("  3 - Open gate 2 (route 2)");
  Serial.println("  t - Test servo sweep");
  Serial.println("  s - Show status");
  Serial.println("===================================");
}

void loop() {
  // 시리얼 명령 수신
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    handleSerialCommand(cmd);
  }
  
  // 각 센서 상태 읽기
  state1 = digitalRead(sensor1);
  state2 = digitalRead(sensor2);
  state3 = digitalRead(sensor3);
  
  // ========== 컨베이어 1 제어 ==========
  if (state1 == LOW) {
    digitalWrite(cmd1Pin, LOW);
    stepper1.stop();
  } else {
    digitalWrite(cmd1Pin, HIGH);
    stepper1.setSpeed(-1300);
    stepper1.runSpeed();
  }
  
  // ========== 컨베이어 2 제어 ==========
  if (state2 == LOW) {
    digitalWrite(cmd2Pin, LOW);
    stepper2.stop();
  } else {
    digitalWrite(cmd2Pin, HIGH);
    stepper2.setSpeed(900);
    stepper2.runSpeed();
  }
  
  // ========== 컨베이어 3 제어 ==========
  if (state3 == LOW) {
    digitalWrite(cmd3Pin, LOW);
    stepper3.stop();
  } else {
    digitalWrite(cmd3Pin, HIGH);
    stepper3.setSpeed(900);
    stepper3.runSpeed();
  }
}

// ========== 시리얼 명령 처리 ==========
void handleSerialCommand(char cmd) {
  switch(cmd) {
    case '1':  // 모든 가림막 닫기 (직진)
      Serial.println(">> Closing all gates (STRAIGHT)");
      gateServo1.write(GATE_CLOSE);
      gateServo2.write(GATE_CLOSE);
      break;
      
    case '2':  // 경로1 가림막 열기
      Serial.println(">> Opening Gate 1 (ROUTE 1)");
      gateServo1.write(GATE_OPEN_1);
      gateServo2.write(GATE_CLOSE);
      break;
      
    case '3':  // 경로2 가림막 열기
      Serial.println(">> Opening Gate 2 (ROUTE 2)");
      gateServo1.write(GATE_CLOSE);
      gateServo2.write(GATE_OPEN_2);
      break;
      
    case 't':  // 서보 테스트 (스윕)
      Serial.println(">> Testing servo sweep...");
      testServoSweep();
      break;
      
    case 's':  // 상태 표시
      showStatus();
      break;
      
    case '\n':
    case '\r':
      // 개행 무시
      break;
      
    default:
      Serial.println("Unknown command");
      break;
  }
}

// ========== 서보 스윕 테스트 ==========
void testServoSweep() {
  Serial.println("Testing Servo 1...");
  
  // 0도에서 180도까지
  for (int angle = 0; angle <= 180; angle += 10) {
    gateServo1.write(angle);
    Serial.print("Angle: ");
    Serial.println(angle);
    delay(200);
  }
  
  delay(500);
  
  // 180도에서 0도까지
  for (int angle = 180; angle >= 0; angle -= 10) {
    gateServo1.write(angle);
    Serial.print("Angle: ");
    Serial.println(angle);
    delay(200);
  }
  
  Serial.println("Testing Servo 2...");
  
  // 0도에서 180도까지
  for (int angle = 0; angle <= 180; angle += 10) {
    gateServo2.write(angle);
    Serial.print("Angle: ");
    Serial.println(angle);
    delay(200);
  }
  
  delay(500);
  
  // 180도에서 0도까지
  for (int angle = 180; angle >= 0; angle -= 10) {
    gateServo2.write(angle);
    Serial.print("Angle: ");
    Serial.println(angle);
    delay(200);
  }
  
  // 초기 위치로 복귀
  gateServo1.write(GATE_CLOSE);
  gateServo2.write(GATE_CLOSE);
  
  Serial.println("Servo test completed!");
}

// ========== 상태 표시 ==========
void showStatus() {
  Serial.println("===== System Status =====");
  Serial.print("Sensor 1: ");
  Serial.println(state1 == LOW ? "DETECTED" : "CLEAR");
  Serial.print("Sensor 2: ");
  Serial.println(state2 == LOW ? "DETECTED" : "CLEAR");
  Serial.print("Sensor 3: ");
  Serial.println(state3 == LOW ? "DETECTED" : "CLEAR");
  Serial.print("Gate 1 Angle: ");
  Serial.println(gateServo1.read());
  Serial.print("Gate 2 Angle: ");
  Serial.println(gateServo2.read());
  Serial.println("========================");
}
