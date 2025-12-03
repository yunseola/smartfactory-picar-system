#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Simple forward movement (timed, no sensor)

import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo, motor

# Motor pins
MOTOR_M1_IN1 = 15
MOTOR_M1_IN2 = 14
MOTOR_M2_IN1 = 12
MOTOR_M2_IN2 = 13

M1_Direction = -1
M2_Direction = -1

# I2C and PCA9685
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x5f)
pca.frequency = 50

# Servo
SERVO_CHANNEL = 0
steer_servo = servo.Servo(
    pca.channels[SERVO_CHANNEL],
    min_pulse=500, max_pulse=2400, actuation_range=180
)

# Motors
motor1 = motor.DCMotor(pca.channels[MOTOR_M1_IN1], pca.channels[MOTOR_M1_IN2])
motor1.decay_mode = motor.SLOW_DECAY
motor2 = motor.DCMotor(pca.channels[MOTOR_M2_IN1], pca.channels[MOTOR_M2_IN2])
motor2.decay_mode = motor.SLOW_DECAY

# Parameters
CENTER = 90
SPEED = 0.18  # Same as line tracking speed
DURATION = 2.0  # Move for 2 seconds

def stop():
    motor1.throttle = 0
    motor2.throttle = 0

def forward(speed):
    motor1.throttle = speed * M1_Direction
    motor2.throttle = speed * M2_Direction

if __name__ == "__main__":
    try:
        print("=== Move Forward (Timed) ===")

        # Center steering
        steer_servo.angle = CENTER
        time.sleep(0.3)

        # Move forward
        print(f"Moving forward for {DURATION} seconds...")
        forward(SPEED)
        time.sleep(DURATION)

        # Stop
        stop()
        print("Done")

    except KeyboardInterrupt:
        pass
    finally:
        stop()
        steer_servo.angle = CENTER
        pca.deinit()
