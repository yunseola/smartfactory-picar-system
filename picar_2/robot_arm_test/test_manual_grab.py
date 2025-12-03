#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Manual grab test - check if hardware can physically grab objects
import sys, time
sys.path.append("/home/pi1/Adeept_PiCar-Pro/Server")
from RPIservo import ServoCtrl

sc = ServoCtrl()
sc.start()
time.sleep(1)

print("=== Manual Grab Test ===\n")
print("Place object in front of gripper and press Enter at each step\n")

# Current angles from servo_config.py
GRIP_OPEN = 130
GRIP_CLOSE = 80
PICK_D_READY = 145
PICK_C_DOWN = 150
PICK_C_LIFT = 120
PICK_D_LIFT = 130

print("Step 1: Initial position")
sc.setPWM(0, 90)   # A center
sc.setPWM(1, 90)   # B center
sc.setPWM(2, 130)  # C neutral
sc.setPWM(3, 90)   # D neutral
sc.setPWM(4, GRIP_OPEN)  # E open
time.sleep(2)

input("Press Enter to continue...")

print("\nStep 2: Set wrist angle")
print(f"Setting D = {PICK_D_READY}")
sc.setPWM(3, PICK_D_READY)
time.sleep(0.5)

input("Is gripper parallel to ground? Press Enter...")

print("\nStep 3: Lower arm")
print(f"Setting C = {PICK_C_DOWN}")
sc.setPWM(2, PICK_C_DOWN)
time.sleep(1)

input("Is gripper above object? Press Enter to close gripper...")

print("\nStep 4: Close gripper")
print(f"Setting E = {GRIP_CLOSE}")
sc.setPWM(4, GRIP_CLOSE)
time.sleep(1)

grabbed = input("\nDid gripper HOLD the object firmly? (y/n): ")

if grabbed.lower() != 'y':
    print("\n[X] HARDWARE ISSUE DETECTED!")
    print("\nPossible causes:")
    print(f"1. GRIP_CLOSE={GRIP_CLOSE} is too large (gripper doesn't close enough)")
    print("   -> Try smaller value like 60 or 50")
    print("2. Gripper servo is weak or damaged")
    print("3. Object is too slippery or smooth")
    print("4. Object is too large for gripper")

    new_close = input(f"\nTry different GRIP_CLOSE value? (current={GRIP_CLOSE}, enter new value or 'n'): ")
    if new_close != 'n':
        GRIP_CLOSE = int(new_close)
        print(f"Testing with GRIP_CLOSE = {GRIP_CLOSE}")
        sc.setPWM(4, GRIP_OPEN)
        time.sleep(0.5)
        sc.setPWM(4, GRIP_CLOSE)
        time.sleep(1)
        grabbed2 = input("Does it hold now? (y/n): ")
        if grabbed2.lower() == 'y':
            print(f"\n[OK] SUCCESS! Update servo_config.py: GRIP_CLOSE = {GRIP_CLOSE}")
else:
    print("\n[OK] Gripper holds object!")

    print("\nStep 5: Lift object")
    print(f"Setting C = {PICK_C_LIFT}, D = {PICK_D_LIFT}")
    sc.setPWM(2, PICK_C_LIFT)
    sc.setPWM(3, PICK_D_LIFT)
    time.sleep(1)

    still_holding = input("Is object still in gripper? (y/n): ")

    if still_holding.lower() == 'y':
        print("\n[OK][OK] HARDWARE IS WORKING!")
        print("Problem is likely SOFTWARE (timing, detection, etc)")
    else:
        print("\n[X] Object dropped during lift!")
        print("Possible causes:")
        print("1. Gripper not tight enough - reduce GRIP_CLOSE more")
        print("2. Wrist angle changed too much during lift")
        print("3. Movement too fast - servo needs more time")

print("\nResetting...")
sc.setPWM(4, GRIP_OPEN)
time.sleep(0.3)
sc.setPWM(2, 130)
sc.setPWM(3, 90)
time.sleep(0.5)

print("Test complete!")
