#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Raw sensor test - check actual GPIO values
import time
import RPi.GPIO as GPIO

PIN_LINE_L = 22
PIN_LINE_M = 27
PIN_LINE_R = 17

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_LINE_L, GPIO.IN)
GPIO.setup(PIN_LINE_M, GPIO.IN)
GPIO.setup(PIN_LINE_R, GPIO.IN)

print("=== Raw GPIO Test ===")
print("Reading direct GPIO values")
print("Try covering sensors with hand or placing on black line")
print("Press Ctrl+C to exit\n")

try:
    while True:
        L = GPIO.input(PIN_LINE_L)
        M = GPIO.input(PIN_LINE_M)
        R = GPIO.input(PIN_LINE_R)

        # Show both raw value and what gpiozero would read
        print(f"RAW: L={L}  M={M}  R={R}  --> ({L},{M},{R})", end="    ")

        # If sensor is active LOW (common for some IR sensors)
        L_inv = 1 - L
        M_inv = 1 - M
        R_inv = 1 - R
        print(f"INVERTED: ({L_inv},{M_inv},{R_inv})", end="\r")

        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nTest stopped")
finally:
    GPIO.cleanup()
