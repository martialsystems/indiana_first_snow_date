# Copyright (c) 2026 Martial Systems LLC
"""Locked first 0.1 in SNOW date vs 1991-2020 median and last year."""

from __future__ import annotations

from pathlib import Path

QUESTION = (
    "Does last year's first 0.1 in GHCND SNOW date beat the 1991-2020 median date "
    "at held-out Indiana GHCND cores?"
)
USER_AGENT = "MartialSystemsResearch/indiana_first_snow_date"
MAX_FIGURES = 2
SNOW_INCH_MIN = 0.1
SNOW_MM_PER_IN = 25.4
COMPLETE_FRAC = 0.80
INDEX_GIST = "https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3"
TEMP_GIST = "https://gist.github.com/martialsystems/e5de316dbb5f672573906572730e3735"

CORE_STATIONS = (
    ("USW00014848", "South Bend"),
    ("USW00014827", "Fort Wayne"),
    ("USW00093819", "Indianapolis"),
    ("USW00093817", "Evansville"),
)
CORE_IDS = tuple(s for s, _ in CORE_STATIONS)
VALPO_ID = "USW00004846"
VALPO_NAME = "Valparaiso"
MICHIGAN_CITY_ID = "USC00125604"

FIRST_SNOW = "first_snow"
TARGETS = (FIRST_SNOW,)

# Winter Y/Y+1 uses season_year Y (1 July Y through 30 June Y+1).
TRAIN_YEARS = tuple(range(1991, 2019))  # through 2018-19
HOLDOUT_YEARS = tuple(range(2019, 2025))  # 2019-20 through 2024-25
CONFIRM_YEAR = 2025  # 2025-26
CLIMATE_FIRST = 1991
CLIMATE_LAST = 2020
MIN_TRAIN_SEASONS = 20

GHCND_STATION_URL = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/{sid}.csv.gz"
GHCND_STATIONS_URL = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
REPO_ROOT = Path(__file__).resolve().parents[2]

PARENT_FREEZE = "28941fb"
PARENT_ENSO = "d861556"
PARENT_DJF = "9aa7935"
PARENT_NWI = "82ce0ce"

LIVE_SCATTER_SUBTITLE = (
    "Holdout season day-of-year from 1 July. Median and last year vs observed. "
    "Days of error, not a frost warning and not season-total inches."
)
LIVE_BARS_SUBTITLE = (
    "Holdout MAE in days. Median vs last year. Days of error, not a frost warning."
)
FIXTURE_SCATTER_SUBTITLE = "Fixture first-snow dates. Does not rescue live skill."
FIXTURE_BARS_SUBTITLE = "Fixture MAE in days. Does not rescue live skill."
