
import requests, sys, json

URL = "http://localhost:8000/predict"  # change host:port if needed
img_path = sys.argv[1]

with open(img_path, "rb") as f:
    files = {"file": (img_path, f, "image/jpeg")}
    r = requests.post(URL, files=files, timeout=30)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))
