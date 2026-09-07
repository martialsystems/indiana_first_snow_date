#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""Live GHCND SNOW first 0.1 in date vs median and last year. Empty core SNOW stops."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from snowdate.errors import FetchError  # noqa: E402
from snowdate.pipeline import run_live  # noqa: E402


def main() -> int:
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "logs" / "in_live"
    cache = Path(sys.argv[2]) if len(sys.argv) > 2 else REPO / "data" / "raw"
    try:
        report = run_live(dest, cache_dir=cache)
    except FetchError as exc:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "fetch_stop.txt").write_text(str(exc) + "\n", encoding="utf-8")
        print(exc)
        return 2
    print(report["question"])
    block = report["holdout_cores"]["by_target"]["first_snow"]
    print(
        "median MAE",
        round(block["median"]["mae_days"], 2),
        "last year MAE",
        round(block["last_year"]["mae_days"], 2),
        "n",
        block["n"],
    )
    print("last_year_beats_median", report["last_year_beats_median"])
    print("used_optional", report.get("used_optional"))
    print(report["figures"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
