import cv2
import os
import numpy as np
from ultralytics import YOLO

VIDEO = "video.mp4"
OUT = "crops"
# Pit polygon in full-frame pixel coords (slanted area). EDIT THESE:
POLY = np.array([[300,400],[1500,350],[1700,800],[200,900]], dtype=np.int32)
SAVE_EVERY_SEC = 0.5

os.makedirs(OUT, exist_ok=True)
model = YOLO("yolov8m.pt")           # pretrained COCO; 'truck' = class 7

cap = cv2.VideoCapture(VIDEO)
fps = cap.get(cv2.CAP_PROP_FPS)
W, H = int(cap.get(3)), int(cap.get(4))
writer = cv2.VideoWriter("tracked.mp4", cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
step = max(1, int(fps * SAVE_EVERY_SEC))

f = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    res = model.track(frame, persist=True, tracker="bytetrack.yaml",
                      classes=[7], conf=0.25, verbose=False)[0]
    cv2.polylines(frame, [POLY], True, (0, 255, 255), 2)

    if res.boxes.id is not None:
        for box, tid in zip(res.boxes.xyxy.cpu().numpy(),
                            res.boxes.id.int().cpu().numpy()):
            x1, y1, x2, y2 = map(int, box)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            if cv2.pointPolygonTest(POLY, (float(cx), float(cy)), False) < 0:
                continue                      # outside the pit zone
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"ID {tid}", (x1, y1 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            if f % step == 0:
                crop = frame[max(0,y1):y2, max(0,x1):x2]
                if crop.size:
                    cv2.imwrite(f"{OUT}/id{tid}_f{f:07d}.jpg", crop)
    writer.write(frame)
    f += 1

cap.release(); writer.release()
print("done")