import sys, time
sys.path.append("/home/pi1/Adeept_PiCar-Pro/Server")
from RPIservo import ServoCtrl

sc = ServoCtrl()
sc.start()
time.sleep(1)

# 채널 매핑 (일반적인 Adeept PiCar-Pro 로봇팔)
# 채널 0: 베이스 회전 (좌우)
# 채널 1: 어깨 (상하)
# 채널 2: 팔꿈치 (상하)
# 채널 3: 손목 (위아래)
# 채널 4: 그리퍼 (개폐)

print("=== 로봇팔 각 관절 테스트 ===\n")

# 1. 초기 위치로 설정 (안전한 중립 위치)
print("1. 초기 위치 설정...")
sc.setPWM(0, 90)   # 베이스 중앙
sc.setPWM(1, 90)   # 어깨 중간
sc.setPWM(2, 90)   # 팔꿈치 중간
sc.setPWM(4, 120)  # 그리퍼 열림
time.sleep(2)

# 2. 베이스 회전 테스트 (채널 0)
print("\n2. 베이스 회전 테스트 (채널 0)...")
for angle in [90, 45, 135, 90]:  # 중앙 -> 왼쪽 -> 오른쪽 -> 중앙
    print(f"   베이스: {angle}도")
    sc.setPWM(0, angle)
    time.sleep(2)

# 3. 어깨 관절 테스트 (채널 1)
print("\n3. 어깨 관절 테스트 (채널 1)...")
for angle in [90, 60, 120, 90]:  # 중앙 -> 위 -> 아래 -> 중앙
    print(f"   어깨: {angle}도")
    sc.setPWM(1, angle)
    time.sleep(2)

# 4. 팔꿈치 관절 테스트 (채널 2)
print("\n4. 팔꿈치 관절 테스트 (채널 2)...")
for angle in [90, 60, 120, 90]:  # 중앙 -> 굽힘 -> 펼침 -> 중앙
    print(f"   팔꿈치: {angle}도")
    sc.setPWM(2, angle)
    time.sleep(2)

# 5. 손목 관절 테스트 (채널 3)
print("\n5. 손목 관절 테스트 (채널 3)...")
for angle in [90, 60, 120, 170, 90]:  # 중앙 -> 위 -> 아래 -> 뒤 -> 중앙
    print(f"   손목: {angle}도")
    sc.setPWM(3, angle)
    time.sleep(2)

# 6. 그리퍼 테스트 (채널 4)
print("\n6. 그리퍼 테스트 (채널 4)...")
for angle in [120, 105, 100, 120]:  # 열림 -> 닫힘 -> 열림
    print(f"   그리퍼: {angle}도")
    sc.setPWM(4, angle)
    time.sleep(2)

# 7. 복합 동작 테스트
print("\n7. 복합 동작 테스트...")
print("   물체 집기 시뮬레이션")

# 위치 이동
sc.setPWM(0, 45)   # 베이스 왼쪽
sc.setPWM(1, 100)  # 어깨 내림
sc.setPWM(2, 100)  # 팔꿈치 펼침
time.sleep(2)

# 그리퍼 닫기
sc.setPWM(4, 100)
time.sleep(1)

# 들어올리기
sc.setPWM(1, 70)
sc.setPWM(2, 80)
time.sleep(2)

# 반대편으로 이동
sc.setPWM(0, 135)
time.sleep(2)

# 놓기
sc.setPWM(4, 120)
time.sleep(1)

# 원위치
sc.setPWM(0, 90)
sc.setPWM(1, 90)
sc.setPWM(2, 90)

print("\n=== 테스트 완료! ===")
