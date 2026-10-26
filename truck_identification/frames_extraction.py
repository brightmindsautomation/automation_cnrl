import cv2, os

VIDEO = "video2.mkv"
OUT = "yolo_frames"
os.makedirs(OUT, exist_ok=True)

cap = cv2.VideoCapture(VIDEO)
fps = cap.get(cv2.CAP_PROP_FPS)
step = 24          # 1 frame per second

i = n = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    if i % step == 0:
        cv2.imwrite(f"{OUT}/f_{i:07d}.jpg", frame)   # full frame, no cropping
        n += 1
    i += 1
print("saved", n)