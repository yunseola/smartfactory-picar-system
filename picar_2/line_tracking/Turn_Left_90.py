#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: Turn_Left_90.py
#
# Purpose: Turn left 90 degrees while moving backward
#
# Action sequence:
#   1) Left steering + backward (90 degree turn)
#   2) Center steering + stop

import time
from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo, motor

# ----------------------------------------------------
# 1) Motor/Servo pins
# ----------------------------------------------------
MOTOR_M1_IN1 = 15
MOTOR_M1_IN2 = 14
MOTOR_M2_IN1 = 12
MOTOR_M2_IN2 = 13

M1_Direction = -1
M2_Direction = -1

# I2C and PCA9685 setup
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x5f)
pca.frequency = 50

# Servo setup (channel 0)
SERVO_CHANNEL = 0
steer_servo = servo.Servo(
    pca.channels[SERVO_CHANNEL],
    min_pulse=500, max_pulse=2400, actuation_range=180
)

# Motor setup
motor1 = motor.DCMotor(pca.channels[MOTOR_M1_IN1], pca.channels[MOTOR_M1_IN2])
motor1.decay_mode = motor.SLOW_DECAY
motor2 = motor.DCMotor(pca.channels[MOTOR_M2_IN1], pca.channels[MOTOR_M2_IN2])
motor2.decay_mode = motor.SLOW_DECAY

# ----------------------------------------------------
# 2) Steering/Speed parameters
# ----------------------------------------------------
CENTER = 90    # Straight
LEFT   = 50    # Left steering
RIGHT  = 130   # Right steering

# Speed/Time for 90 degree turn (backward while turning)
BACK_SPEED = 0.2    # Backward speed (reduced for smooth motion)
BACK_TIME  = 3.0    # Backward time (increased due to lower speed)

# ----------------------------------------------------
# Utility functions
# ----------------------------------------------------
def steer(angle):
    steer_servo.angle = angle
    print(f"[STEER] {angle:.1f}")

def backward(p):
    motor1.throttle = -p * M1_Direction
    motor2.throttle = -p * M2_Direction
    print(f"[BACK] pwm={p:.2f}")

def stop():
    motor1.throttle = 0
    motor2.throttle = 0
    print("[STOP]")

# ----------------------------------------------------
# 3) Core: 90 degree left turn function
# ----------------------------------------------------
def turn_left_90():
    print("=== TURN LEFT 90 (BACKWARD) ===")

    # 0) Initial stop & center steering
    stop()
    steer(CENTER)
    time.sleep(0.3)

    # 1) Left steering + backward (90 degree turn while moving backward)
    print("LEFT + BACKWARD (90 turn)")
    steer(LEFT)
    time.sleep(0.2)
    backward(BACK_SPEED)
    time.sleep(BACK_TIME)
    stop()
    time.sleep(0.3)

    # 2) Return steering to center
    steer(CENTER)
    time.sleep(0.2)

    print("=== TURN LEFT 90 DONE ===")

# ----------------------------------------------------
# 4) Main
# ----------------------------------------------------
if __name__ == "__main__":
    try:
        print("Test before: lift wheels off ground recommended!")
        time.sleep(1.5)
        turn_left_90()
    except KeyboardInterrupt:
        pass
    finally:
        stop()
        steer(CENTER)
        pca.deinit()
        print("Clean exit.")
