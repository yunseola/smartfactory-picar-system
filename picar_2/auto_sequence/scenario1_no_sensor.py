#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scenario1_no_sensor.py
#
# Scenario without line tracking sensors (TIMER-BASED)
# 1) Backward (timed)
# 2) Turn left 90
# 3) Place in box
# 4) Turn right 90 (return)
# 5) Forward (timed)

import time
import subprocess

# Script paths
TURN_LEFT_90_PATH  = "/home/pi1/Adeept_PiCar-Pro/line_tracking/Turn_Left_90.py"
TURN_RIGHT_90_PATH = "/home/pi1/Adeept_PiCar-Pro/line_tracking/Turn_Return_90.py"
PLACE_IN_BOX_PATH  = "/home/pi1/Adeept_PiCar-Pro/inductor_project/place_in_box.py"

# Simple forward/backward scripts (we'll create these)
MOVE_BACKWARD_PATH = "/home/pi1/Adeept_PiCar-Pro/line_tracking/move_backward_timed.py"
MOVE_FORWARD_PATH  = "/home/pi1/Adeept_PiCar-Pro/line_tracking/move_forward_timed.py"

def run_script(path, timeout=None):
    """Run python script as subprocess"""
    print(f"\n[RUN] {path} (timeout={timeout})")

    proc = subprocess.Popen(["python3", path],
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           text=True)

    if timeout is None:
        stdout, stderr = proc.communicate()
        if proc.returncode == 0:
            print(f"[END] {path} (success)")
        else:
            print(f"[ERROR] {path} exit code: {proc.returncode}")
            if stderr:
                print(f"Error: {stderr}")
    else:
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
            print(f"[END] {path} (finished before timeout)")
        except subprocess.TimeoutExpired:
            print(f"[TIMEOUT] {path} -> terminate")
            proc.terminate()
            try:
                proc.wait(timeout=2.0)
                print(f"[END] {path} (terminated)")
            except subprocess.TimeoutExpired:
                print(f"[KILL] {path} force kill")
                proc.kill()
                proc.wait()

    time.sleep(0.5)

def main():
    print("Test: lift wheels off ground first!")
    time.sleep(2.0)

    print("\n" + "="*60)
    print("=== Scenario: NO SENSOR (timer-based) ===")
    print("="*60 + "\n")

    try:
        # STEP 1) Backward (timed)
        print("\n" + "-"*60)
        print("[STEP 1/5] Backward (timed)")
        print("-"*60)
        run_script(MOVE_BACKWARD_PATH, timeout=None)
        print("[STEP 1/5] Done\n")
        time.sleep(1.0)

        # STEP 2) Turn left 90
        print("\n" + "-"*60)
        print("[STEP 2/5] Turn left 90")
        print("-"*60)
        run_script(TURN_LEFT_90_PATH)
        print("[STEP 2/5] Done\n")
        time.sleep(1.0)

        # STEP 3) Place in box
        print("\n" + "-"*60)
        print("[STEP 3/5] Place in box")
        print("-"*60)
        run_script(PLACE_IN_BOX_PATH)
        print("[STEP 3/5] Done\n")
        time.sleep(1.0)

        # STEP 4) Turn right 90
        print("\n" + "-"*60)
        print("[STEP 4/5] Turn right 90")
        print("-"*60)
        run_script(TURN_RIGHT_90_PATH)
        print("[STEP 4/5] Done\n")
        time.sleep(1.0)

        # STEP 5) Forward (timed)
        print("\n" + "-"*60)
        print("[STEP 5/5] Forward (timed)")
        print("-"*60)
        run_script(MOVE_FORWARD_PATH, timeout=None)
        print("[STEP 5/5] Done\n")

        print("\n" + "="*60)
        print("=== ALL DONE ===")
        print("="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\n[!] Stopped (Ctrl+C)")
    except Exception as e:
        print(f"\n\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
