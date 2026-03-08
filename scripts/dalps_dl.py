\
#!/usr/bin/env python3
dALPS step 2: Slice QC (CNN) + ROI detection (YOLOv5) + boundary CSV.

Pipeline:
1) Resize PNGs -> work/resized_png/
2) CNN inference -> keep prediction==1 -> work/png_yes/
3) YOLOv5 detect two ROIs (class 0 / class 1)
4) Within each ROI, apply simple color thresholds to find green/blue boundary cues
5) Save output_boundary_coordinates.csv

Notes
- This script does NOT change the original PNGs. All intermediate files go to work_dir.
- CNN / YOLO weights are expected to be placed in ./models/ by default.
- If you prefer a local YOLOv5 repo (no torch.hub download), pass --yolov5-repo.

Coordinate system
- Coordinates are in PNG pixel space.
- The downstream FSL extraction assumes the PNG pixel space matches NIfTI voxel x/y (after rotate_k90).
  Please validate on a few subjects by visual inspection.

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import torch
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from tqdm import tqdm


def resize_images(input_dir: Path, output_dir: Path, size=(224, 224)) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for p in input_dir.glob("*.png"):
        img = Image.open(p)
        img = img.resize(size, Image.LANCZOS)
        img.save(output_dir / p.name)


def predict_with_cnn(model_path: Path, image_dir: Path) -> pd.DataFrame:
    model = load_model(str(model_path))
    filenames = sorted([p.name for p in image_dir.glob("*.png")])
    rows = []
    for fn in tqdm(filenames, desc="CNN"):
        img_path = image_dir / fn
        img = load_img(img_path, target_size=(224, 224))
        arr = img_to_array(img).reshape(1, 224, 224, 3)
        prob = model.predict(arr, verbose=0)
        pred = int(np.round(prob).item())
        rows.append((fn, float(np.squeeze(prob)), pred))
    return pd.DataFrame(rows, columns=["filename", "probability", "prediction"])


def copy_yes_pngs(pred_df: pd.DataFrame, src_dir: Path, dst_dir: Path) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    yes = pred_df[pred_df["prediction"] == 1]["filename"].tolist()
    for fn in tqdm(yes, desc="Copy yes"):
        shutil.copy(src_dir / fn, dst_dir / fn)


def load_yolov5(yolo_weights: Path, device: str, yolov5_repo: str | None) -> "torch.nn.Module":
    if yolov5_repo:
        # local repo clone
        model = torch.hub.load(yolov5_repo, "custom", path=str(yolo_weights), source="local", device=device)
    else:
        # will download yolov5 from GitHub on first run
        model = torch.hub.load("ultralytics/yolov5", "custom", path=str(yolo_weights))
        model.to(device)
    return model


def detect_boundaries(
    model,
    image_dir: Path,
    rect_out_dir: Path,
    out_csv: Path,
    device: str,
) -> None:
    rect_out_dir.mkdir(parents=True, exist_ok=True)

    # OpenCV reads BGR. Thresholds below are legacy values.
    lower_green = np.array([0, 130, 0], dtype=np.uint8)
    upper_green = np.array([80, 255, 80], dtype=np.uint8)
    lower_blue = np.array([140, 70, 0], dtype=np.uint8)
    upper_blue = np.array([220, 200, 60], dtype=np.uint8)

    output_rows = []
    for img_path in tqdm(sorted(image_dir.glob("*.png")), desc="YOLO"):
        filename = img_path.name
        img = cv2.imread(str(img_path))
        if img is None:
            raise RuntimeError(f"Failed to read image: {img_path}")

        results = model(str(img_path))
        pred = results.xyxy[0]  # (N,6): xmin,ymin,xmax,ymax,conf,cls

        # default = zeros (match legacy fillna->0)
        cls0 = [0, 0, 0, 0, 0, 0]  # xmin,ymin,xmax,ymax,green_max,blue_min
        cls1 = [0, 0, 0, 0, 0, 0]  # xmin,ymin,xmax,ymax,blue_max,green_min

        for row in pred:
            xmin, ymin, xmax, ymax, conf, cls = row
            cls_i = int(cls.item()) if hasattr(cls, "item") else int(cls)
            xmin = int(round(float(xmin)))
            ymin = int(round(float(ymin)))
            xmax = int(round(float(xmax)))
            ymax = int(round(float(ymax)))

            # clamp
            xmin = max(0, xmin); ymin = max(0, ymin)
            xmax = min(img.shape[1], xmax); ymax = min(img.shape[0], ymax)
            if xmax <= xmin or ymax <= ymin:
                continue

            rect_img = img[ymin:ymax, xmin:xmax]
            rect_image_filename = f"{filename}_class_{cls_i}.png"
            cv2.imwrite(str(rect_out_dir / rect_image_filename), rect_img)

            green_mask = cv2.inRange(rect_img, lower_green, upper_green)
            blue_mask = cv2.inRange(rect_img, lower_blue, upper_blue)
            green_coords = np.argwhere(green_mask > 0)
            blue_coords = np.argwhere(blue_mask > 0)
            if green_coords.size == 0 or blue_coords.size == 0:
                continue

            if cls_i == 0:
                green_max_x = int(np.max(green_coords[:, 1]))
                blue_min_x = int(np.min(blue_coords[:, 1]))
                cls0 = [xmin, ymin, xmax, ymax, green_max_x, blue_min_x]
            elif cls_i == 1:
                blue_max_x = int(np.max(blue_coords[:, 1]))
                green_min_x = int(np.min(green_coords[:, 1]))
                cls1 = [xmin, ymin, xmax, ymax, blue_max_x, green_min_x]

        output_rows.append([filename] + cls0 + cls1)

    columns = [
        "filename",
        "xmin_0", "ymin_0", "xmax_0", "ymax_0", "green_max_0", "blue_min_0",
        "xmin_1", "ymin_1", "xmax_1", "ymax_1", "blue_max_1", "green_min_1",
    ]
    df = pd.DataFrame(output_rows, columns=columns)
    df.to_csv(out_csv, index=False)
    print(f"Saved: {out_csv}")


def main() -> None:
    ap = argparse.ArgumentParser(description="dALPS DL step: CNN QC + YOLO ROI + boundary CSV.")
    ap.add_argument("--png-dir", required=True, type=Path, help="Directory containing input PNG slices.")
    ap.add_argument("--work-dir", default=Path("work"), type=Path, help="Working directory for intermediates.")
    ap.add_argument("--cnn-weights", default=Path("models/dALPS_CNN.h5"), type=Path, help="CNN .h5 weights path.")
    ap.add_argument("--yolo-weights", default=Path("models/dALPS_YoloV5.pt"), type=Path, help="YOLOv5 .pt weights path.")
    ap.add_argument("--yolov5-repo", default=None, help="Optional: local yolov5 repo path.")
    ap.add_argument("--device", default="cuda:0", help="cuda:0 / cpu etc.")
    args = ap.parse_args()

    resized_dir = args.work_dir / "resized_png"
    yes_dir = args.work_dir / "png_yes"
    rect_dir = args.work_dir / "rect_images"
    args.work_dir.mkdir(parents=True, exist_ok=True)

    # 1) resize
    resize_images(args.png_dir, resized_dir)

    # 2) cnn filter
    pred_df = predict_with_cnn(args.cnn_weights, resized_dir)
    pred_csv = args.work_dir / "predictions.csv"
    pred_df.to_csv(pred_csv, index=False)
    copy_yes_pngs(pred_df, args.png_dir, yes_dir)

    # 3) yolo boundaries
    yolo = load_yolov5(args.yolo_weights, device=args.device, yolov5_repo=args.yolov5_repo)
    out_csv = args.work_dir / "output_boundary_coordinates.csv"
    detect_boundaries(yolo, yes_dir, rect_dir, out_csv, device=args.device)


if __name__ == "__main__":
    main()
