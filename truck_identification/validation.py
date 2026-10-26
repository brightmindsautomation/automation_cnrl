import cv2
from ultralytics import YOLO

MODEL = "best.pt"
VIDEO = "video.mp4"
OUT = "output.mp4"

model = YOLO(MODEL)
cap = cv2.VideoCapture(VIDEO)
fps = cap.get(cv2.CAP_PROP_FPS)
w, h = int(cap.get(3)), int(cap.get(4))
writer = cv2.VideoWriter(OUT, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

while True:
    ok, frame = cap.read()
    if not ok:
        break
    res = model.predict(frame, conf=0.25, imgsz=640, device="cpu", verbose=False)[0]
    writer.write(res.plot())     # frame with boxes, class names and confidences

cap.release()
writer.release()
print("saved", OUT)