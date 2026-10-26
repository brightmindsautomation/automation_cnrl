from ultralytics import YOLO

model = YOLO("yolov8m.pt")
model.train(
    data="dataset/data.yaml",
    epochs=100,
    imgsz=960,
    batch=4,
    patience=0,      # don't stop early, validation is too small to trust
)