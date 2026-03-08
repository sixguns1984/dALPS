\
#!/usr/bin/env python3
dALPS step 4: Calculate per-slice ALPS and aggregate per-subject ALPS.

Input: output.csv from FSL extraction (step 3)
Columns:
  filename,value1..value8

Output:
  - (optional) writes back an updated per-slice csv with ALPS_right/ALPS_left
  - writes per-subject ALPS.csv with columns: id,aver

Aggregation rule (legacy-compatible):
  - For each subject:
      - take mean of non-zero ALPS_right across slices
      - take mean of non-zero ALPS_left across slices
      - final = mean of (right_avg, left_avg) if both non-zero,
                else sum (only one side),
                else 0.

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser(description="Compute ALPS.csv from step-3 output.csv.")
    ap.add_argument("--input-csv", required=True, type=Path, help="Step-3 output.csv")
    ap.add_argument("--out-subject-csv", required=True, type=Path, help="Per-subject ALPS.csv output path")
    ap.add_argument("--out-slice-csv", default=None, type=Path, help="Optional: write per-slice CSV with ALPS columns")
    args = ap.parse_args()

    df = pd.read_csv(args.input_csv).fillna(0)

    def safe_div(num, den):
        return (num / den) if den != 0 else 0

    df["ALPS_right"] = df.apply(
        lambda r: safe_div(r["value1"] + r["value2"], r["value3"] + r["value4"]) if (r["value1"] != 0) else 0,
        axis=1,
    )
    df["ALPS_left"] = df.apply(
        lambda r: safe_div(r["value5"] + r["value6"], r["value7"] + r["value8"]) if (r["value5"] != 0) else 0,
        axis=1,
    )

    # subject id: filename split by '_' take first token (legacy behavior)
    df["id"] = df["filename"].astype(str).str.split("_").str[0]

    # aggregate
    out_rows = []
    for sid, g in df.groupby("id"):
        r = g.loc[g["ALPS_right"] != 0, "ALPS_right"]
        l = g.loc[g["ALPS_left"] != 0, "ALPS_left"]
        r_avg = float(r.mean()) if len(r) else 0.0
        l_avg = float(l.mean()) if len(l) else 0.0

        if r_avg != 0 and l_avg != 0:
            aver = (r_avg + l_avg) / 2.0
        elif r_avg != 0 or l_avg != 0:
            aver = r_avg + l_avg
        else:
            aver = 0.0
        out_rows.append((sid, aver))

    args.out_subject_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(out_rows, columns=["id", "aver"]).to_csv(args.out_subject_csv, index=False)

    if args.out_slice_csv:
        args.out_slice_csv.parent.mkdir(parents=True, exist_ok=True)
        df.drop(columns=["id"]).to_csv(args.out_slice_csv, index=False)

    print(f"Saved per-subject: {args.out_subject_csv}")
    if args.out_slice_csv:
        print(f"Saved per-slice: {args.out_slice_csv}")


if __name__ == "__main__":
    main()
