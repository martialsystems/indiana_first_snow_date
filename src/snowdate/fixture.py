# Copyright (c) 2026 Martial Systems LLC
"""Synthetic first-snow dates. Does not rescue live skill."""

from __future__ import annotations

import numpy as np

from snowdate.config import CONFIRM_YEAR, CORE_STATIONS, FIRST_SNOW, VALPO_ID, VALPO_NAME
from snowdate.dates import date_from_season_doy
from snowdate.pack import DatePack

_COORDS = {
    "USW00014848": (41.71, -86.32, "South Bend"),
    "USW00014827": (41.12, -85.19, "Fort Wayne"),
    "USW00093819": (39.72, -86.29, "Indianapolis"),
    "USW00093817": (38.04, -87.53, "Evansville"),
    VALPO_ID: (41.45, -87.00, VALPO_NAME),
}

# Season-doy from 1 July: north earlier (late Oct ~123), south later (late Nov ~150).
_MEAN = {
    "USW00014848": 123,
    "USW00014827": 130,
    "USW00093819": 145,
    "USW00093817": 155,
    VALPO_ID: 120,
}


def build_fixture(*, seed: int = 7) -> DatePack:
    rng = np.random.default_rng(seed)
    stations = list(CORE_STATIONS) + [(VALPO_ID, VALPO_NAME)]
    rows: dict[str, list] = {
        "station_id": [],
        "name": [],
        "lat": [],
        "lon": [],
        "target": [],
        "season_year": [],
        "obs_date": [],
        "complete_frac": [],
    }
    years = list(range(1991, CONFIRM_YEAR + 1))
    for sid, name in stations:
        lat, lon, label = _COORDS[sid]
        thin = sid == VALPO_ID
        for y in years:
            doy = int(min(300, max(40, round(_MEAN[sid] + rng.normal(0.0, 8.0)))))
            obs = date_from_season_doy(doy, int(y))
            rows["station_id"].append(sid)
            rows["name"].append(label)
            rows["lat"].append(lat)
            rows["lon"].append(lon)
            rows["target"].append(FIRST_SNOW)
            rows["season_year"].append(int(y))
            rows["obs_date"].append(obs)
            rows["complete_frac"].append(0.45 if thin else 0.95)
    for i, (sid, y) in enumerate(zip(rows["station_id"], rows["season_year"])):
        if sid == "USW00093817" and y == 2003:
            rows["complete_frac"][i] = 0.50
    return DatePack(
        station_id=np.array(rows["station_id"], dtype=object),
        name=np.array(rows["name"], dtype=object),
        lat=np.array(rows["lat"], dtype=float),
        lon=np.array(rows["lon"], dtype=float),
        target=np.array(rows["target"], dtype=object),
        season_year=np.array(rows["season_year"], dtype=int),
        obs_date=np.array(rows["obs_date"], dtype=object),
        complete_frac=np.array(rows["complete_frac"], dtype=float),
        source="fixture",
        extra={"planted": True, "thin_optional": VALPO_ID, "mc_in_core_mean": False},
    )
