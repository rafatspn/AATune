#!/usr/bin/env python3
"""
extract_top_configs.py

Filter a CSV of OpenMP experiment results to the fastest 10 % runs for a
given executable, then save *all* unique configuration values
(OMP_NUM_THREADS, OMP_PROC_BIND, OMP_SCHEDULE) to a JSON file.

Example
-------
python extract_top_configs.py results.csv my_kernel -o top_configs.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import pandas as pd


def extract_top_configs(csv_path: Path, executable_name: str, output_json: Path):
    df = pd.read_csv(csv_path)
    required_cols = {"Executable",
                     "OMP_NUM_THREADS",
                     "OMP_PROC_BIND",
                     "OMP_SCHEDULE",
                     "Execution Time (s)"}
    missing = required_cols.difference(df.columns)
    if missing:
        raise ValueError(
            f"{csv_path} is missing column(s): {', '.join(missing)}"
        )

    # Find the column to filter all the entries
    subset = df[df["Executable"] == executable_name].copy()
    if subset.empty:
        raise ValueError(f"No rows found for executable '{executable_name}'")

    # Select top 10%
    subset = subset.sort_values("Execution Time (s)", ascending=True)
    n_top = max(1, math.ceil(0.10 * len(subset)))
    top_subset = subset.head(n_top)

    # Select unique values to form subset
    result = {
        "OMP_NUM_THREADS": sorted(map(int,
                                    top_subset["OMP_NUM_THREADS"].unique())),
        "OMP_PROC_BIND":  sorted(map(str,
                                    top_subset["OMP_PROC_BIND"].unique())),
        "OMP_SCHEDULE":   sorted(map(str,
                                    top_subset["OMP_SCHEDULE"].unique())),
    }


    # Save json file
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w") as fp:
        json.dump(result, fp, indent=4)

    return result


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Extract unique OpenMP settings from the top‑10 % ""fastest runs of a specified executable.")
    parser.add_argument("-csv", type=Path, help="CSV file containing the experiment results.")
    parser.add_argument("-executable", type=str, help="Exact name of the executable to filter on.")
    parser.add_argument("-o", "--output-json", type=Path, default=Path("top_configs.json"), help="Path for the generated JSON file ""(default: %(default)s).")
    return parser


def main():
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        configs = extract_top_configs(
            csv_path=args.csv,
            executable_name=args.executable,
            output_json=args.output_json
        )
    except Exception as exc:
        parser.error(str(exc))

    print(f"Unique configuration values saved to '{args.output_json}':")
    print(json.dumps(configs, indent=4))


if __name__ == "__main__": 
    main()
