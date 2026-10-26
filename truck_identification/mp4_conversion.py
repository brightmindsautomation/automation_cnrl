import cv2

SRC = "./feeds/video3_wet.mkv"
DST = "./feeds/video3_wet.mp4"

cap = cv2.VideoCapture(SRC)
if not cap.isOpened():
    raise SystemExit("Could not open " + SRC)

fps = cap.get(cv2.CAP_PROP_FPS) or 25
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

writer = cv2.VideoWriter(DST, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

i = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    writer.write(frame)
    i += 1
    if i % 500 == 0:
        print(f"{i}/{total} frames")

cap.release()
writer.release()
print("saved", DST)