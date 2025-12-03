#include <AccelStepper.h>

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

#define motorInterfaceType 1

// AccelStepper 객체 생성
AccelStepper stepper1 = AccelStepper(motorInterfaceType, step1Pin, dir1Pin);
AccelStepper stepper2 = AccelStepper(motorInterfaceType, step2Pin, dir2Pin);
AccelStepper stepper3 = AccelStepper(motorInterfaceType, step3Pin, dir3Pin);

// 센서 상태 변수
int state1, state2, state3;

void setup() {
  Serial.begin(115200);
  
  // ========== 컨베이어 1 설정 (제조사 방식 그대로) ==========
  pinMode(enable1Pin, OUTPUT);
  pinMode(sensor1, INPUT_PULLUP);
  pinMode(cmd1Pin, OUTPUT);
  
  digitalWrite(enable1Pin, LOW);
  digitalWrite(cmd1Pin, HIGH);
  digitalWrite(sensor1, HIGH);
  
  stepper1.setMaxSpeed(1000);
  stepper1.setSpeed(900);
  
  // ========== 컨베이어 2 설정 (동일한 방식) ==========
  pinMode(enable2Pin, OUTPUT);
  pinMode(sensor2, INPUT_PULLUP);
  pinMode(cmd2Pin, OUTPUT);
  
  digitalWrite(enable2Pin, LOW);
  digitalWrite(cmd2Pin, HIGH);
  digitalWrite(sensor2, HIGH);
  
  stepper2.setMaxSpeed(1000);
  stepper2.setSpeed(900);
  
  // ========== 컨베이어 3 설정 (동일한 방식) ==========
  pinMode(enable3Pin, OUTPUT);
  pinMode(sensor3, INPUT_PULLUP);
  pinMode(cmd3Pin, OUTPUT);
  
  digitalWrite(enable3Pin, LOW);
  digitalWrite(cmd3Pin, HIGH);
  digitalWrite(sensor3, HIGH);
  
  stepper3.setMaxSpeed(1000);
  stepper3.setSpeed(900);
  
  Serial.println("3 Conveyors Ready");
}

void loop() {
  // 각 센서 상태 읽기
  state1 = digitalRead(sensor1);
  state2 = digitalRead(sensor2);
  state3 = digitalRead(sensor3);
  
  // ========== 컨베이어 1 제어 (제조사 로직 그대로) ==========
  if (state1 == LOW) {
    digitalWrite(cmd1Pin, LOW);
    stepper1.stop();
  } else {
    digitalWrite(cmd1Pin, HIGH);
    stepper1.setSpeed(900);
    stepper1.runSpeed();
  }
  
  // ========== 컨베이어 2 제어 (동일한 로직) ==========
  if (state2 == LOW) {
    digitalWrite(cmd2Pin, LOW);
    stepper2.stop();
  } else {
    digitalWrite(cmd2Pin, HIGH);
    stepper2.setSpeed(900);
    stepper2.runSpeed();
  }
  
  // ========== 컨베이어 3 제어 (동일한 로직) ==========
  if (state3 == LOW) {
    digitalWrite(cmd3Pin, LOW);
    stepper3.stop();
  } else {
    digitalWrite(cmd3Pin, HIGH);
    stepper3.setSpeed(900);
    stepper3.runSpeed();
  }
}