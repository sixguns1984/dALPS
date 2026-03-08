\
#!/usr/bin/env bash
set -euo pipefail

# dALPS step 3 (FSL): read output_boundary_coordinates.csv and compute mean tensor components in ROIs.
#
# Requirements:
#   - FSL installed and in PATH (fslmaths, fslstats)
#   - subjects_root/<SUBJ>/ contains:
#       <SUBJ>_FA.nii.gz
#       vol0000.nii.gz
#       vol0003.nii.gz
#       vol0005.nii.gz
#
# Output:
#   output.csv columns:
#     filename,value1,value2,value3,value4,value5,value6,value7,value8
#
# Notes:
#   - This script assumes PNG coords map to voxel coords used by FSL -roi.
#   - It parses:
#       SUBJ = filename without .png, then remove trailing _<slice>
#       Z    = trailing digits before .png (slice index)

usage() {
  cat <<EOF
Usage:
  bash scripts/dalps_fsl_extract.sh \\
    --boundary_csv work/output_boundary_coordinates.csv \\
    --subjects_root /path/to/subjects_root \\
    --out_csv outputs/output.csv

Optional:
  --fa_suffix _FA.nii.gz   (default)
EOF
}

BOUNDARY_CSV=""
SUBJECTS_ROOT=""
OUT_CSV=""
FA_SUFFIX="_FA.nii.gz"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --boundary_csv) BOUNDARY_CSV="$2"; shift 2;;
    --subjects_root) SUBJECTS_ROOT="$2"; shift 2;;
    --out_csv) OUT_CSV="$2"; shift 2;;
    --fa_suffix) FA_SUFFIX="$2"; shift 2;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

if [[ -z "${BOUNDARY_CSV}" || -z "${SUBJECTS_ROOT}" || -z "${OUT_CSV}" ]]; then
  usage; exit 1
fi

mkdir -p "$(dirname "${OUT_CSV}")"
echo "filename,value1,value2,value3,value4,value5,value6,value7,value8" > "${OUT_CSV}"

tail -n +2 "${BOUNDARY_CSV}" | while IFS=, read -r filename xmin_0 ymin_0 xmax_0 ymax_0 green_max_0 blue_min_0 xmin_1 ymin_1 xmax_1 ymax_1 blue_max_1 green_min_1; do
  # Parse subject + slice
  base="${filename%.png}"
  subj="${base%_*}"
  zmin="$(echo "$filename" | grep -oP '\d+(?=\.[^.]+$)' || true)"
  if [[ -z "${zmin}" ]]; then
    echo "WARN: cannot parse slice index from filename=${filename}, set zmin=0" >&2
    zmin=0
  fi

  subj_dir="${SUBJECTS_ROOT}/${subj}"
  fa="${subj}${FA_SUFFIX}"

  value1=0; value2=0; value3=0; value4=0
  value5=0; value6=0; value7=0; value8=0

  # ---------- RIGHT (class 0) ----------
  if [[ "${xmin_0}" != "0" || "${ymin_0}" != "0" || "${xmax_0}" != "0" || "${ymax_0}" != "0" || "${green_max_0}" != "0" || "${blue_min_0}" != "0" ]]; then
    xmin_r1=$(echo "${xmin_0} + ${blue_min_0} + 1" | bc)
    xmin_r2=$(echo "${xmin_0} + 1" | bc)
    xsize_r1=$(echo "${xmax_0} - ${blue_min_0} - ${xmin_0} + 1" | bc)
    xsize_r2=$(echo "${green_max_0} + 1" | bc)
    ysize_r=$(echo "${ymax_0} - ${ymin_0}" | bc)
    ymin_r=$(echo "${ymin_0} + 1" | bc)

    if [[ "${xsize_r1}" -gt 0 && "${xsize_r2}" -gt 0 && "${ysize_r}" -gt 0 ]]; then
      pushd "${subj_dir}" >/dev/null
      rm -f "${subj}_FA_mask"* || true

      fslmaths "${fa}" -roi "${xmin_r1}" "${xsize_r1}" "${ymin_r}" "${ysize_r}" "${zmin}" 3 0 1 "${subj}_FA_mask_r1.nii.gz"
      fslmaths "${fa}" -roi "${xmin_r2}" "${xsize_r2}" "${ymin_r}" "${ysize_r}" "${zmin}" 3 0 1 "${subj}_FA_mask_r2.nii.gz"
      fslmaths "${subj}_FA_mask_r1.nii.gz" -bin "${subj}_FA_mask_r1_bin.nii.gz"
      fslmaths "${subj}_FA_mask_r2.nii.gz" -bin "${subj}_FA_mask_r2_bin.nii.gz"

      value1=$(fslstats vol0000.nii.gz -k "${subj}_FA_mask_r1_bin.nii.gz" -M || echo 0)
      value2=$(fslstats vol0000.nii.gz -k "${subj}_FA_mask_r2_bin.nii.gz" -M || echo 0)
      value3=$(fslstats vol0003.nii.gz -k "${subj}_FA_mask_r1_bin.nii.gz" -M || echo 0)
      value4=$(fslstats vol0005.nii.gz -k "${subj}_FA_mask_r2_bin.nii.gz" -M || echo 0)

      rm -f "${subj}_FA_mask"* || true
      popd >/dev/null
    fi
  fi

  # ---------- LEFT (class 1) ----------
  if [[ "${xmin_1}" != "0" || "${ymin_1}" != "0" || "${xmax_1}" != "0" || "${ymax_1}" != "0" || "${blue_max_1}" != "0" || "${green_min_1}" != "0" ]]; then
    xmin_l2=$(echo "${xmin_1} + ${green_min_1} + 1" | bc)
    xmin_l1=$(echo "${xmin_1} + 1" | bc)
    xsize_l2=$(echo "${xmax_1} - ${green_min_1} - ${xmin_1} + 1" | bc)
    xsize_l1=$(echo "${blue_max_1} + 1" | bc)
    ysize_l=$(echo "${ymax_1} - ${ymin_1}" | bc)
    ymin_l=$(echo "${ymin_1} + 1" | bc)

    if [[ "${xsize_l1}" -gt 0 && "${xsize_l2}" -gt 0 && "${ysize_l}" -gt 0 ]]; then
      pushd "${subj_dir}" >/dev/null
      rm -f "${subj}_FA_mask"* || true

      fslmaths "${fa}" -roi "${xmin_l1}" "${xsize_l1}" "${ymin_l}" "${ysize_l}" "${zmin}" 3 0 1 "${subj}_FA_mask_l1.nii.gz"
      fslmaths "${fa}" -roi "${xmin_l2}" "${xsize_l2}" "${ymin_l}" "${ysize_l}" "${zmin}" 3 0 1 "${subj}_FA_mask_l2.nii.gz"
      fslmaths "${subj}_FA_mask_l1.nii.gz" -bin "${subj}_FA_mask_l1_bin.nii.gz"
      fslmaths "${subj}_FA_mask_l2.nii.gz" -bin "${subj}_FA_mask_l2_bin.nii.gz"

      value5=$(fslstats vol0000.nii.gz -k "${subj}_FA_mask_l1_bin.nii.gz" -M || echo 0)
      value6=$(fslstats vol0000.nii.gz -k "${subj}_FA_mask_l2_bin.nii.gz" -M || echo 0)
      value7=$(fslstats vol0003.nii.gz -k "${subj}_FA_mask_l1_bin.nii.gz" -M || echo 0)
      value8=$(fslstats vol0005.nii.gz -k "${subj}_FA_mask_l2_bin.nii.gz" -M || echo 0)

      rm -f "${subj}_FA_mask"* || true
      popd >/dev/null
    fi
  fi

  echo "${filename},${value1},${value2},${value3},${value4},${value5},${value6},${value7},${value8}" >> "${OUT_CSV}"
done

echo "Done. Saved: ${OUT_CSV}"
