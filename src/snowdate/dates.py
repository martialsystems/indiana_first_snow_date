# Copyright (c) 2026 Martial Systems LLC
"""Season day-of-year from 1 July so last year is a seasonal lag, not a calendar wrap."""

from __future__ import annotations

from datetime import date, timedelta


def season_start(year: int) -> date:
    return date(int(year), 7, 1)


def season_end(year: int) -> date:
    return date(int(year) + 1, 6, 30)


def season_doy(d: date, year: int) -> int:
    return (d - season_start(year)).days + 1


def date_from_season_doy(doy: float, year: int) -> date:
    n = int(round(float(doy)))
    start = season_start(year)
    end = season_end(year)
    n = min((end - start).days + 1, max(1, n))
    return start + timedelta(days=n - 1)


def error_days(pred: date, obs: date, year: int) -> int:
    return season_doy(pred, year) - season_doy(obs, year)


def iso(d: date) -> str:
    return d.isoformat()


def month_day(d: date) -> str:
    return f"{d.month:02d}-{d.day:02d}"
