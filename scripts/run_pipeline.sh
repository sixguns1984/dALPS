\
#!/usr/bin/env bash
set -euo pipefail

# One-command example pipeline.
# Edit paths below, or use configs/example_config.yaml with your own runner.

IDS="examples/id.txt"
V1_DIR="/path/to/native_space_v1_files"
SUBJECTS_ROOT="/path/to/subjects_root"
CNN="models/dALPS_CNN.h5"
YOLO="models/dALPS_YoloV5.pt"

WORK="work"
OUT="outputs"

python scripts/dalps_nii2png.py --ids "${IDS}" --v1-dir "${V1_DIR}" --out-dir "${WORK}/png"

python scripts/dalps_dl.py --png-dir "${WORK}/png" --work-dir "${WORK}" --cnn-weights "${CNN}" --yolo-weights "${YOLO}" --device "cuda:0"

bash scripts/dalps_fsl_extract.sh --boundary_csv "${WORK}/output_boundary_coordinates.csv" --subjects_root "${SUBJECTS_ROOT}" --out_csv "${OUT}/output.csv"

python scripts/dalps_calculate_alps.py --input-csv "${OUT}/output.csv" --out-subject-csv "${OUT}/ALPS.csv" --out-slice-csv "${OUT}/output_with_alps.csv"
