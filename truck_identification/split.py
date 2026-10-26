import os, shutil, re

SRC = "annot"            # folder containing images/ and labels/
OUT = "dataset"
VAL_FRACTION = 0.2

def frame_no(name):
    return int(re.findall(r"(\d+)", name.split("-", 1)[-1])[-1])

imgs = sorted(os.listdir(f"{SRC}/images"), key=frame_no)
cut = int(len(imgs) * (1 - VAL_FRACTION))

for split, files in (("train", imgs[:cut]), ("valid", imgs[cut:])):
    os.makedirs(f"{OUT}/{split}/images", exist_ok=True)
    os.makedirs(f"{OUT}/{split}/labels", exist_ok=True)
    for f in files:
        shutil.copy(f"{SRC}/images/{f}", f"{OUT}/{split}/images/{f}")
        lbl = os.path.splitext(f)[0] + ".txt"
        if os.path.exists(f"{SRC}/labels/{lbl}"):
            shutil.copy(f"{SRC}/labels/{lbl}", f"{OUT}/{split}/labels/{lbl}")

with open(f"{OUT}/data.yaml", "w") as fh:
    fh.write("path: .\ntrain: train/images\nval: valid/images\n"
             "names:\n  0: approach\n  1: idle\n  2: raise\n")