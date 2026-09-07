#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from snowdate.pipeline import stage0_fixture  # noqa: E402


def main() -> int:
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "logs" / "stage0_fixture"
    report = stage0_fixture(dest)
    print(report["question"])
    block = report["holdout_cores"]["by_target"]["first_snow"]
    print("median MAE", block["median"]["mae_days"], "last year MAE", block["last_year"]["mae_days"])
    print(report["figures"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
