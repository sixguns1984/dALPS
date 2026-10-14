\
#!/usr/bin/env python3
"""
dALPS step 1: Convert native-space V1 NIfTI (<ID>_V1.nii.gz) to per-slice RGB PNGs.

The legacy script wrote intermediate TXT files and looped voxel-by-voxel (slow).
This version is vectorized and CLI-friendly.

Output naming (default):
    <ID>_<slice_index>.png   where slice_index is Z index (0-based)

Note on orientation:
    The legacy code applied np.rot90(image, k=1) before saving.
    To stay compatible, default rotate_k90=1 (same behavior).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import nibabel as nib
import numpy as np
from PIL import Image
from tqdm import tqdm


def load_ids(ids_txt: Path) -> list[str]:
    ids = []
    for line in ids_txt.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if s:
            ids.append(s)
    return ids


def v1_to_pngs(v1_path: Path, out_dir: Path, subject_id: str, rotate_k90: int = 1) -> int:
    img = nib.load(str(v1_path))
    data = img.get_fdata()  # expected shape: (X, Y, Z, 3)
    if data.ndim != 4 or data.shape[-1] != 3:
        raise ValueError(f"Unexpected V1 shape {data.shape}. Expected (X,Y,Z,3). File={v1_path}")

    # abs + scale to [0,255]
    rgb = np.clip(np.abs(data) * 255.0, 0, 255).astype(np.uint8)  # (X,Y,Z,3)

    n_slices = rgb.shape[2]
    saved = 0
    for z in range(n_slices):
        sl = rgb[:, :, z, :]  # (X,Y,3)
        if rotate_k90:
            sl = np.rot90(sl, k=rotate_k90)
        # PIL expects (H,W,3) - here X,Y are arbitrary; np.rot90 already swaps axes
        Image.fromarray(sl, mode="RGB").save(out_dir / f"{subject_id}_{z}.png")
        saved += 1
    return saved


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert V1 NIfTI to per-slice RGB PNGs.")
    ap.add_argument("--ids", required=True, type=Path, help="Path to id.txt (one subject id per line).")
    ap.add_argument("--v1-dir", required=True, type=Path, help="Directory containing <ID>_V1.nii.gz files.")
    ap.add_argument("--out-dir", required=True, type=Path, help="Output directory for PNG slices.")
    ap.add_argument("--rotate-k90", type=int, default=1, help="Number of 90° rotations (default=1, legacy-compatible).")
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    ids = load_ids(args.ids)

    total = 0
    for sid in tqdm(ids, desc="Subjects"):
        v1_path = args.v1_dir / f"{sid}_V1.nii.gz"
        if not v1_path.exists():
            raise FileNotFoundError(f"Missing file: {v1_path}")
        total += v1_to_pngs(v1_path, args.out_dir, sid, rotate_k90=args.rotate_k90)

    print(f"Done. Saved {total} PNG slices to: {args.out_dir}")


if __name__ == "__main__":
    main()
