#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test with pull-up/pull-down resistors
import time
import RPi.GPIO as GPIO

PIN_LINE_L = 22
PIN_LINE_M = 27
PIN_LINE_R = 17

print("=== Testing with PULL-UP resistors ===\n")

# Setup GPIO with PULL-UP
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_LINE_L, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_LINE_M, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIN_LINE_R, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("With PULL-UP (should read 1 if floating):")
time.sleep(0.5)

try:
    for i in range(10):
        L = GPIO.input(PIN_LINE_L)
        M = GPIO.input(PIN_LINE_M)
        R = GPIO.input(PIN_LINE_R)
        print(f"  L={L}  M={M}  R={R}")
        time.sleep(0.3)

    print("\n=== Testing with PULL-DOWN resistors ===\n")

    # Reset and setup with PULL-DOWN
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_LINE_L, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(PIN_LINE_M, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(PIN_LINE_R, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    print("With PULL-DOWN (should read 0 if floating):")
    time.sleep(0.5)

    for i in range(10):
        L = GPIO.input(PIN_LINE_L)
        M = GPIO.input(PIN_LINE_M)
        R = GPIO.input(PIN_LINE_R)
        print(f"  L={L}  M={M}  R={R}")
        time.sleep(0.3)

except KeyboardInterrupt:
    print("\n\nTest stopped")
finally:
    GPIO.cleanup()

print("\n=== Results ===")
print("If values are ALWAYS 0 with pull-up: Sensor output is stuck LOW")
print("If values are ALWAYS 1 with pull-down: Sensor output is stuck HIGH")
print("If values change: Sensor might be working but needs correct resistor")
