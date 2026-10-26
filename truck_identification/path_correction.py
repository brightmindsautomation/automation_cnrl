import os

root = os.path.abspath("dataset")
with open("dataset/data.yaml", "w") as f:
    f.write(f'path: "{root}"\n'
            "train: train/images\n"
            "val: valid/images\n"
            "names:\n  0: approach\n  1: idle\n  2: raise\n")
print(root)
for p in ("train/images", "valid/images"):
    print(p, len(os.listdir(os.path.join(root, p))), "images")