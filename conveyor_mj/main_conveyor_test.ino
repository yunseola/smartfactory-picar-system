#include <AccelStepper.h>

#define enablePin 4
#define dirxPin 3
#define stepxPin 2
#define motorInterfaceType 1
#define cmdxPin 13
#define sensorx 22

// Create a new instance of the AccelStepper class:
AccelStepper stepperx = AccelStepper(motorInterfaceType, stepxPin, dirxPin);

int statex;

void setup()
{  
  pinMode(enablePin, OUTPUT);
  pinMode(sensorx, INPUT_PULLUP);
  pinMode(cmdxPin, OUTPUT);

  digitalWrite(enablePin, LOW);
  digitalWrite(cmdxPin, HIGH);
  digitalWrite(sensorx, HIGH);

  stepperx.setMaxSpeed(1000);
  stepperx.setSpeed(900);
}

void loop()
{  
   statex = digitalRead(sensorx);

   if (statex == LOW) {
    digitalWrite(cmdxPin, LOW);
    stepperx.stop();
   } else {
    digitalWrite(cmdxPin, HIGH);
    stepperx.setSpeed(900);  
    stepperx.runSpeed();
   }
}