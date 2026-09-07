# Copyright (c) 2026 Martial Systems LLC

from datetime import date, timedelta

from snowdate.labels import first_snow_date, snow_mm_to_inches


def test_tenth_inch_is_254_mm() -> None:
    assert abs(snow_mm_to_inches(2.54) - 0.1) < 1e-9
    assert snow_mm_to_inches(3.0) >= 0.1
    assert snow_mm_to_inches(2.0) < 0.1


def test_first_snow_is_first_hit_on_or_after_1_july() -> None:
    start = date(2018, 7, 1)
    end = date(2019, 6, 30)
    filled = []
    d = start
    while d <= end:
        inches = 0.5 if d == date(2018, 11, 12) else 0.0
        filled.append((d, inches))
        d += timedelta(days=1)
    filled.append((date(2018, 6, 20), 2.0))
    obs, frac, reason = first_snow_date(filled, year=2018)
    assert reason == "ok"
    assert obs == date(2018, 11, 12)
    assert frac >= 0.80


def test_june_snow_belongs_to_prior_winter() -> None:
    start = date(2018, 7, 1)
    end = date(2019, 6, 30)
    filled = []
    d = start
    while d <= end:
        inches = 0.5 if d == date(2019, 1, 4) else 0.0
        filled.append((d, inches))
        d += timedelta(days=1)
    obs, _, reason = first_snow_date(filled, year=2018)
    assert reason == "ok"
    assert obs == date(2019, 1, 4)


def test_trace_below_tenth_is_not_measurable() -> None:
    start = date(2018, 7, 1)
    end = date(2019, 6, 30)
    filled = []
    d = start
    while d <= end:
        inches = 0.05 if d == date(2018, 11, 1) else (0.4 if d == date(2018, 12, 1) else 0.0)
        filled.append((d, inches))
        d += timedelta(days=1)
    obs, _, reason = first_snow_date(filled, year=2018)
    assert reason == "ok"
    assert obs == date(2018, 12, 1)


def test_incomplete_window_drops() -> None:
    days = [(date(2018, 11, 1), 0.5)]
    obs, frac, reason = first_snow_date(days, year=2018)
    assert obs is None
    assert reason == "incomplete"
    assert frac < 0.80
