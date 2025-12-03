#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Direct gripper test - manual control

import sys, time
sys.path.append("/home/pi1/Adeept_PiCar-Pro/Server")
from RPIservo import ServoCtrl

sc = ServoCtrl()
sc.start()
time.sleep(1)

SERVO_E = 4

print("="*50)
print("=== Direct Gripper Control Test ===")
print("="*50)
print()
print("Testing gripper movement with multiple commands...")
print()

# Test 1: Open to 120
print("TEST 1: Opening to 120 degrees (3 times)")
for i in range(3):
    print(f"  Command {i+1}: setPWM(SERVO_E, 120)")
    sc.setPWM(SERVO_E, 120)
    time.sleep(0.5)
print("  Waiting 3 seconds...")
time.sleep(3)
print("  -> Is gripper OPEN? (wide)")
input("Press Enter to continue...")

# Test 2: Close to 45
print("\nTEST 2: Closing to 45 degrees (3 times)")
for i in range(3):
    print(f"  Command {i+1}: setPWM(SERVO_E, 45)")
    sc.setPWM(SERVO_E, 45)
    time.sleep(0.5)
print("  Waiting 3 seconds...")
time.sleep(3)
print("  -> Is gripper CLOSED? (tight)")
input("Press Enter to continue...")

# Test 3: Open again
print("\nTEST 3: Opening to 120 degrees again")
for i in range(3):
    print(f"  Command {i+1}: setPWM(SERVO_E, 120)")
    sc.setPWM(SERVO_E, 120)
    time.sleep(0.5)
print("  Waiting 3 seconds...")
time.sleep(3)
print("  -> Is gripper OPEN again?")
input("Press Enter to continue...")

# Test 4: Try different angles
print("\nTEST 4: Testing range 30 -> 150")
angles = [30, 60, 90, 120, 150]
for angle in angles:
    print(f"  Setting to {angle} degrees...")
    sc.setPWM(SERVO_E, angle)
    time.sleep(2)
    print(f"  -> Current angle should be {angle}")

print("\n" + "="*50)
print("Test complete!")
print("="*50)
print("\nDid the gripper move at all during these tests?")
print("1. If YES: gripper works, problem is in main code logic")
print("2. If NO: gripper servo might be disconnected or broken")
