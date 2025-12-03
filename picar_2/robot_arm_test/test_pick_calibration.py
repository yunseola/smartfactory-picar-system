# test_pick_calibration.py
# 물건 집기 최적 각도 찾기 스크립트
import sys, time
sys.path.append("/home/pi1/Adeept_PiCar-Pro/Server")
from RPIservo import ServoCtrl

sc = ServoCtrl()
sc.start()
time.sleep(1)

print("=== 물건 집기 캘리브레이션 ===\n")
print("물건을 카메라 앞 바닥에 놓아주세요.\n")

# 테스트할 각도 범위
C_angles = [130, 135, 140, 145, 150, 155, 160]  # C 각도 후보
D_angles = [120, 130, 140, 145, 150, 155]       # D 각도 후보

print("1. 초기 위치로 이동")
sc.setPWM(0, 90)   # A 중앙
sc.setPWM(1, 90)   # B 중앙
sc.setPWM(2, 130)  # C 시작
sc.setPWM(3, 90)   # D 중립
sc.setPWM(4, 130)  # 집게 벌림
time.sleep(2)

print("\n2. C 각도 테스트 (팔 높이)")
print("각 각도에서 집게가 물건 바로 위에 오는지 확인하세요")
print("D는 145도로 고정합니다 (집게가 바닥과 평행하도록)\n")

for c in C_angles:
    input(f"C={c}도로 이동하려면 Enter를 누르세요...")
    sc.setPWM(3, 145)  # D를 먼저 설정
    time.sleep(0.3)
    sc.setPWM(2, c)    # C 이동
    time.sleep(1)
    print(f"현재: C={c}, D=145")
    print("  → 집게가 물건 바로 위에 있나요?")
    print("  → 집게가 바닥과 평행한가요?")
    print()

print("\n3. D 각도 미세 조정")
print("가장 적절했던 C 각도를 사용해서 D를 조정합니다\n")
best_c = int(input("가장 적절했던 C 각도는? (예: 150): "))

print(f"\nC={best_c}로 고정하고, D 각도를 변경합니다\n")
for d in D_angles:
    input(f"D={d}도로 이동하려면 Enter를 누르세요...")
    sc.setPWM(2, best_c)  # C 고정
    sc.setPWM(3, d)       # D 변경
    time.sleep(1)
    print(f"현재: C={best_c}, D={d}")
    print("  → 집게가 바닥과 평행한가요?")
    print("  → 이 각도로 물건을 집을 수 있을 것 같나요?")
    print()

best_d = int(input("\n가장 적절한 D 각도는? (예: 145): "))

print(f"\n4. 최종 테스트: C={best_c}, D={best_d}")
print("실제 집기 동작을 시뮬레이션합니다\n")

input("시작하려면 Enter를 누르세요...")

# 실제 집기 시뮬레이션
print("집게 벌리기...")
sc.setPWM(4, 130)
time.sleep(0.5)

print(f"손목을 {best_d}도로...")
sc.setPWM(3, best_d)
time.sleep(0.3)

print(f"팔을 {best_c}도로 내리기...")
sc.setPWM(2, best_c)
time.sleep(0.8)

print("집게 닫기...")
sc.setPWM(4, 80)
time.sleep(0.8)

print("들어올리기...")
sc.setPWM(2, 120)
sc.setPWM(3, 130)
time.sleep(0.5)

success = input("\n물건을 성공적으로 집었나요? (y/n): ")

if success.lower() == 'y':
    print("\n✅ 성공! servo_config.py에 다음 값을 설정하세요:")
    print(f"PICK_C_DOWN = {best_c}")
    print(f"PICK_D_READY = {best_d}")
    print(f"PICK_C_LIFT = 120")
    print(f"PICK_D_LIFT = 130")
else:
    print("\n❌ 실패. 다시 테스트를 실행하거나 각도를 조정해보세요.")
    print("팁:")
    print("  - C 값이 너무 크면 팔이 너무 뒤로 감 (줄이세요)")
    print("  - C 값이 너무 작으면 팔이 물건에 닿지 않음 (늘리세요)")
    print("  - D 값으로 집게의 기울기를 조절하세요")

print("\n원위치로 복귀...")
sc.setPWM(4, 130)
time.sleep(0.3)
sc.setPWM(2, 130)
sc.setPWM(3, 90)
time.sleep(0.5)

print("테스트 완료!")
