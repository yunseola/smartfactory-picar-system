#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test gripper movement

import sys, time
sys.path.append("/home/pi1/Adeept_PiCar-Pro/Server")
from RPIservo import ServoCtrl

sc = ServoCtrl()
sc.start()
time.sleep(1)

SERVO_E = 4

print("=== Gripper Test ===")
print("Testing angles: 60, 90, 120, 150")
print()

angles = [60, 90, 120, 150, 120, 90, 60, 90]

for angle in angles:
    print(f"Setting gripper to {angle} degrees...")
    sc.setPWM(SERVO_E, angle)
    time.sleep(2)

print("\nTest complete!")
print("Did the gripper move? (y/n)")
