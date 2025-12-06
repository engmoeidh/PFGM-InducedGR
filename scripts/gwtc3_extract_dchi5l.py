#!/usr/bin/env python3
"""
Extract PN dchi5l posteriors from IGWN-GWTC3-TGR-v1-par HDF5 files
and summarise them in a CSV.

Usage
-----
    python scripts/gwtc3_extract_dchi5l.py \\
        /path/to/IGWN-GWTC3-TGR-v1-par \\
        input/reference/par_dchi5l_summary_gwtc3.csv

Input
-----
data_dir : directory containing subfolder "par" with many HDF5 files,
           including the *_dchi5l.h5 PN-test files.

Output
------
out_csv : CSV with columns
    s_event_id     : e.g. "S200225q"
    event_id       : (left None, later filled by fit script)
    filename       : HDF5 file name
    posterior_len  : number of samples
    dchi5l_median  : median of samples
    dchi5l_q05     : 5th percentile
    dchi5l_q95     : 95th percentile
"""

import sys
import os
import glob
import re
import numpy as np
import pandas as pd
import h5py


def find_dchi5l_dataset(h5):
    """Return path of the dchi5l dataset inside an IGWN HDF5 file."""
    candidates = []

    def visitor(name, obj):
        if isinstance(obj, h5py.Dataset):
            nm = name.lower()
            if ("dchi5l" in nm) or (("delta" in nm) and ("5l" in nm) and ("phi" in nm)):
                if obj.dtype.kind in ("f", "i", "u") and obj.ndim == 1 and obj.size >= 100:
                    candidates.append(name)

    h5.visititems(visitor)
    if not candidates:
        return None
    exact = [c for c in candidates if os.path.basename(c).lower() == "dchi5l"]
    if exact:
        return exact[0]
    return sorted(candidates, key=len)[0]


def parse_ids_from_filename(fname: str):
    """
    Extract S-ID from file name like 'par_S200225q_seobnr_dchi5l.h5' -> 'S200225q'.
    """
    base = os.path.basename(fname)
    m = re.match(r"par_(S\\d{6}[a-z]{0,2})_.*_dchi5l\\.h5$", base)
    return m.group(1) if m else None


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    data_dir = os.path.abspath(sys.argv[1])
    out_csv = os.path.abspath(sys.argv[2])

    h5_glob = os.path.join(data_dir, "par", "*_dchi5l.h5")
    h5_files = sorted(glob.glob(h5_glob))

    if not h5_files:
        print(f"[ERROR] No files matching {h5_glob}")
        sys.exit(2)

    rows = []
    for fp in h5_files:
        print(f"[INFO] Reading {fp}")
        try:
            with h5py.File(fp, "r") as h5:
                ds_path = find_dchi5l_dataset(h5)
                if ds_path is None:
                    print(f"[WARN] No dchi5l-like dataset in {fp}")
                    continue
                samples = np.array(h5[ds_path], dtype=float)
                samples = samples[np.isfinite(samples)]
                if samples.size == 0:
                    print(f"[WARN] Empty/NaN samples for {fp}")
                    continue

                med = np.median(samples)
                q05, q95 = np.percentile(samples, [5.0, 95.0])
                s_id = parse_ids_from_filename(fp)

                rows.append(
                    dict(
                        s_event_id=s_id,
                        event_id=None,  # filled later
                        filename=os.path.basename(fp),
                        posterior_len=int(samples.size),
                        dchi5l_median=med,
                        dchi5l_q05=q05,
                        dchi5l_q95=q95,
                    )
                )
        except Exception as exc:
            print(f"[ERROR] {fp}: {exc}")

    df = pd.DataFrame(rows).sort_values("filename").reset_index(drop=True)
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"[OK] Wrote {out_csv} with {len(df)} rows.")


if __name__ == "__main__":
    main()
