# -*- coding: utf-8 -*-
import sys
sys.path.append('/home/pi/Adeept_PiCar-Pro/server/')
from servo import Servo
import time

scGear = Servo()

TEST_B = 100
TEST_C_SAFE = 30
TEST_C_DOWN = 130
TEST_D = 90

print("1. Direction test")
scGear.moveServoB(TEST_B)
time.sleep(2)

print("2. Safe height test")
scGear.moveServoC(TEST_C_SAFE)
time.sleep(2)

print("3. Drop height test")
scGear.moveServoC(TEST_C_DOWN)
time.sleep(2)

print("4. Wrist angle test")
scGear.moveServoD(TEST_D)
time.sleep(2)
EOF