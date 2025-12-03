#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Sensor test script
import time
from gpiozero import InputDevice

PIN_LINE_L = 22
PIN_LINE_M = 27
PIN_LINE_R = 17

sen_left  = InputDevice(PIN_LINE_L)
sen_mid   = InputDevice(PIN_LINE_M)
sen_right = InputDevice(PIN_LINE_R)

print("=== Line Sensor Test ===")
print("Black line = 1, White floor = 0")
print("Press Ctrl+C to exit\n")

try:
    while True:
        L = int(sen_left.value)
        M = int(sen_mid.value)
        R = int(sen_right.value)

        print(f"L={L}  M={M}  R={R}  --> ({L},{M},{R})", end="\r")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\nTest stopped")
finally:
    sen_left.close()
    sen_mid.close()
    sen_right.close()
