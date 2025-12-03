import sys, time
sys.path.append("/home/pi1/Adeept_PiCar-Pro/Server")
from RPIservo import ServoCtrl

sc = ServoCtrl()
sc.start()
time.sleep(1)

print("채널 4 테스트 시작...")
for angle in [120, 105, 100]:
    print(f"→ {angle}도")  # 들여쓰기 4칸 (또는 탭 1개)
    sc.setPWM(4, angle)     # 들여쓰기 4칸
    time.sleep(2)           # 들여쓰기 4칸
    
print("완료!")
