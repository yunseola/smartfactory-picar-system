#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scenario_simple.py
#
# Simple scenario without line sensors:
# 1) Backward (timed)
# 2) Rotate robot arm B channel left 90°
# 3) Place object in box
# 4) Rotate robot arm B channel back to center
# 5) Forward (timed) - return to start

import time
import sys
sys.path.append("/home/pi1/Adeept_PiCar-Pro/Server")

from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo, motor
from RPIservo import ServoCtrl

print("="*60)
print("=== Simple Scenario (No Sensors) ===")
print("="*60)

# ----------------------------------------------------
# 1) Hardware Setup - Motors
# ----------------------------------------------------
MOTOR_M1_IN1 = 15
MOTOR_M1_IN2 = 14
MOTOR_M2_IN1 = 12
MOTOR_M2_IN2 = 13

M1_Direction = 1
M2_Direction = 1

i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c, address=0x5f)
pca.frequency = 50

# Steering servo
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

# ----------------------------------------------------
# 2) Parameters
# ----------------------------------------------------
CENTER = 90
SPEED = 0.18
MOVE_TIME = 2.0  # seconds

# Robot arm servo channels
SERVO_B = 1  # Base rotation (left/right)
SERVO_C = 2  # Height (up/down)
SERVO_D = 3  # Wrist
SERVO_E = 4  # Gripper

# Robot arm angles
B_CENTER = 90   # Center position
B_LEFT_90 = 0   # Left 90 degrees (adjust if needed)

# From servo_config.py
GRIP_OPEN = 120
BOX_C_SAFE = 140
BOX_C_DOWN = 120
BOX_D_ANGLE = 90

# ----------------------------------------------------
# 3) Motor Control Functions
# ----------------------------------------------------
def stop_motors():
    motor1.throttle = 0
    motor2.throttle = 0

def forward(speed):
    motor1.throttle = speed * M1_Direction
    motor2.throttle = speed * M2_Direction

def backward(speed):
    motor1.throttle = -speed * M1_Direction
    motor2.throttle = -speed * M2_Direction

# ----------------------------------------------------
# 4) Robot Arm Functions
# ----------------------------------------------------
def init_arm():
    """Initialize robot arm servo controller"""
    sc = ServoCtrl()
    sc.start()
    time.sleep(0.5)

    # Set initial gripper position (closed at 90 degrees)
    print("  Setting initial gripper position (90 degrees)...")
    sc.setPWM(SERVO_E, 90)
    time.sleep(0.5)

    return sc

def rotate_arm_left(sc):
    """Rotate arm base (B channel) 90 degrees left"""
    print("  Rotating arm base LEFT 90 degrees...")
    sc.setPWM(SERVO_B, B_LEFT_90)
    time.sleep(1.5)  # Wait for rotation to complete

    print("  Opening gripper (90 -> 120 degrees)...")
    sc.setPWM(SERVO_E, 120)
    time.sleep(0.5)  # Wait for gripper to open

def rotate_arm_center(sc):
    """Rotate arm base (B channel) back to center"""
    print("  Rotating arm base back to CENTER...")
    sc.setPWM(SERVO_B, B_CENTER)
    time.sleep(1.5)  # Wait for rotation to complete

def place_object(sc):
    """Place object in box"""
    print("  Moving arm to safe height...")
    sc.setPWM(SERVO_C, BOX_C_SAFE)
    sc.setPWM(SERVO_D, BOX_D_ANGLE)
    time.sleep(0.5)

    print("  Lowering arm to box...")
    sc.setPWM(SERVO_C, BOX_C_DOWN)
    time.sleep(0.8)

    print("  Opening gripper to release object...")
    sc.setPWM(SERVO_E, GRIP_OPEN)
    time.sleep(0.8)

    print("  Raising arm back up...")
    sc.setPWM(SERVO_C, BOX_C_SAFE)
    time.sleep(0.5)

# ----------------------------------------------------
# 5) Main Scenario
# ----------------------------------------------------
def main():
    print("\nWarning: Test with wheels off ground first!")
    print("Press Ctrl+C to stop at any time\n")
    time.sleep(2.0)

    # Initialize robot arm
    print("\n[INIT] Initializing robot arm...")
    sc = init_arm()

    # Center steering
    steer_servo.angle = CENTER
    time.sleep(0.3)

    try:
        # STEP 1: Move backward
        print("\n" + "-"*60)
        print("[STEP 1/5] Moving BACKWARD for {} seconds...".format(MOVE_TIME))
        print("-"*60)
        backward(SPEED)
        time.sleep(MOVE_TIME)
        stop_motors()
        print("[STEP 1/5] Backward complete\n")
        time.sleep(1.0)

        # STEP 2: Rotate arm left 90 degrees
        print("\n" + "-"*60)
        print("[STEP 2/5] Rotating arm LEFT 90 degrees...")
        print("-"*60)
        rotate_arm_left(sc)
        print("[STEP 2/5] Rotation complete\n")
        time.sleep(0.5)

        # STEP 3: Place object in box
        print("\n" + "-"*60)
        print("[STEP 3/5] Placing object in box...")
        print("-"*60)
        place_object(sc)
        print("[STEP 3/5] Object placed\n")
        time.sleep(0.5)

        # STEP 4: Rotate arm back to center
        print("\n" + "-"*60)
        print("[STEP 4/5] Rotating arm back to CENTER...")
        print("-"*60)
        rotate_arm_center(sc)
        print("[STEP 4/5] Arm returned to center\n")
        time.sleep(1.0)

        # STEP 5: Move forward (return to start)
        print("\n" + "-"*60)
        print("[STEP 5/5] Moving FORWARD for {} seconds...".format(MOVE_TIME))
        print("-"*60)
        forward(SPEED)
        time.sleep(MOVE_TIME)
        stop_motors()
        print("[STEP 5/5] Forward complete\n")

        print("\n" + "="*60)
        print("=== SCENARIO COMPLETE ===")
        print("="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\n[!] Stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\n[CLEANUP] Stopping motors and resetting...")
        stop_motors()
        steer_servo.angle = CENTER
        sc.setPWM(SERVO_B, B_CENTER)  # Return arm to center
        pca.deinit()
        print("Done")

if __name__ == "__main__":
    main()
