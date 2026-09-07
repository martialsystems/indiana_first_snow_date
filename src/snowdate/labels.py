# Copyright (c) 2026 Martial Systems LLC
"""First 0.1 in GHCND SNOW on 1 July Y through 30 June Y+1. Not SNWD, PRCP, or TMIN."""

from __future__ import annotations

from datetime import date
from typing import Iterable

from snowdate.config import COMPLETE_FRAC, FIRST_SNOW, SNOW_INCH_MIN, SNOW_MM_PER_IN
from snowdate.dates import season_end, season_start

Daily = list[tuple[date, float]]


def snow_mm_to_inches(mm: float) -> float:
    return float(mm) / SNOW_MM_PER_IN


def window_bounds(year: int) -> tuple[date, date]:
    return season_start(year), season_end(year)


def _max_by_day(days: Iterable[tuple[date, float]]) -> dict[date, float]:
    out: dict[date, float] = {}
    for d, inches in days:
        prev = out.get(d)
        out[d] = inches if prev is None else max(prev, inches)
    return out


def first_snow_date(
    days: Daily,
    *,
    year: int,
    floor: float = COMPLETE_FRAC,
    inch_min: float = SNOW_INCH_MIN,
) -> tuple[date | None, float, str]:
    """Return (date or None, completeness, reason)."""
    start, end = window_bounds(year)
    expected = (end - start).days + 1
    by_day = _max_by_day((d, t) for d, t in days if start <= d <= end)
    frac = len(by_day) / float(expected) if expected else 0.0
    if frac < floor:
        return None, frac, "incomplete"
    hits = [d for d, t in sorted(by_day.items()) if t >= inch_min]
    if not hits:
        return None, frac, "no_snow_in_window"
    return hits[0], frac, "ok"


def season_years_in(days: Daily) -> set[int]:
    years: set[int] = set()
    for d, _ in days:
        years.add(d.year if d.month >= 7 else d.year - 1)
    return years


def require_first_snow_target(target: str) -> None:
    if target != FIRST_SNOW:
        raise ValueError(f"unknown target {target}")
