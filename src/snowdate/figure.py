# Copyright (c) 2026 Martial Systems LLC
"""Two figures: holdout scatter, per-station MAE bars."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from snowdate.claims import require_clean
from snowdate.config import (
    CORE_STATIONS,
    FIRST_SNOW,
    FIXTURE_BARS_SUBTITLE,
    FIXTURE_SCATTER_SUBTITLE,
    LIVE_BARS_SUBTITLE,
    LIVE_SCATTER_SUBTITLE,
    MAX_FIGURES,
)
from snowdate.dates import season_doy
from snowdate.errors import FigureCapError


def bar_station_labels(by_st: dict[str, Any]) -> tuple[list[str], list[str]]:
    order: list[str] = []
    labels: list[str] = []
    for sid, city in CORE_STATIONS:
        if sid in by_st:
            order.append(sid)
            labels.append(city)
    return order, labels


def _cap(n: int) -> None:
    if n > MAX_FIGURES:
        raise FigureCapError(f"this tree stops at {MAX_FIGURES} figures")


def write_scatter(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig1_title")
    require_clean(subtitle, source="fig1_sub")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = [r for r in fit["holdout_rows"] if r["target"] == FIRST_SNOW]
    fig, ax = plt.subplots(figsize=(6.4, 5.2))
    obs = np.array([r["obs_season_doy"] for r in rows], dtype=float)
    med = np.array([r["median_season_doy"] for r in rows], dtype=float)
    ly = np.array([r["last_year_season_doy"] for r in rows], dtype=float)
    ax.scatter(obs, med, s=28, c="#64748b", marker="o", label="1991-2020 median", zorder=2)
    ax.scatter(obs, ly, s=28, c="#b45309", marker="x", label="last year", zorder=3)
    if obs.size:
        lo = float(np.nanmin([obs.min(), med.min(), ly.min()]))
        hi = float(np.nanmax([obs.max(), med.max(), ly.max()]))
    else:
        lo, hi = 1.0, 200.0
    pad = 0.05 * (hi - lo + 1.0)
    ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], color="#0f172a", lw=1.0, label="1:1")
    ax.set_xlabel("observed season day-of-year (from 1 July)")
    ax.set_ylabel("predicted season day-of-year")
    ax.set_title("First 0.1 in SNOW", fontsize=10)
    ax.legend(fontsize=7, loc="upper left")
    fig.suptitle(title, fontsize=11)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.subplots_adjust(bottom=0.18, top=0.88)
    fig.text(0.5, 0.04, subtitle, ha="center", fontsize=8)
    fig.savefig(dest, dpi=130, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return dest


def draw_bars(fit: dict[str, Any], *, title: str, subtitle: str):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    by_st = fit["holdout_cores"]["by_station"]
    order, labels = bar_station_labels(by_st)
    x = np.arange(len(order), dtype=float)
    width = 0.35
    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    med = [by_st[sid][FIRST_SNOW]["median"]["mae_days"] for sid in order]
    ly = [by_st[sid][FIRST_SNOW]["last_year"]["mae_days"] for sid in order]
    ax.bar(x - width / 2, med, width, color="#64748b", label="1991-2020 median")
    ax.bar(x + width / 2, ly, width, color="#b45309", label="last year")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8, rotation=28, ha="right")
    ax.set_ylabel("MAE (days)")
    ax.set_title("First 0.1 in SNOW", fontsize=10)
    ax.legend(fontsize=7, loc="upper right")
    ax.tick_params(axis="x", pad=2)
    fig.suptitle(title, fontsize=11)
    fig.subplots_adjust(bottom=0.28, top=0.86)
    fig.text(0.5, 0.03, subtitle, ha="center", fontsize=8)
    return fig


def write_bars(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig2_title")
    require_clean(subtitle, source="fig2_sub")
    import matplotlib.pyplot as plt

    fig = draw_bars(fit, title=title, subtitle=subtitle)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=130, bbox_inches="tight", pad_inches=0.22)
    plt.close(fig)
    return dest


def write_two(log_dir: Path, *, fit: dict[str, Any], live: bool) -> list[str]:
    _cap(2)
    log_dir.mkdir(parents=True, exist_ok=True)
    scatter = write_scatter(
        log_dir / "scatter.png",
        fit=fit,
        title="Holdout first 0.1 in SNOW dates",
        subtitle=LIVE_SCATTER_SUBTITLE if live else FIXTURE_SCATTER_SUBTITLE,
    )
    bars = write_bars(
        log_dir / "mae_bars.png",
        fit=fit,
        title="Per-station holdout MAE",
        subtitle=LIVE_BARS_SUBTITLE if live else FIXTURE_BARS_SUBTITLE,
    )
    paths = [scatter, bars]
    _cap(len(paths))
    return [p.name for p in paths]
