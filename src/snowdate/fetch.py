# Copyright (c) 2026 Martial Systems LLC
"""Live GHCND SNOW. Empty core stops. Thin Valparaiso is logged and dropped. Michigan City stays out."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import numpy as np

from snowdate.config import (
    COMPLETE_FRAC,
    CORE_IDS,
    CORE_STATIONS,
    FIRST_SNOW,
    MICHIGAN_CITY_ID,
    MIN_TRAIN_SEASONS,
    VALPO_ID,
    VALPO_NAME,
)
from snowdate.errors import FetchError
from snowdate.ghcnd import load_station_inventory, load_station_snow
from snowdate.http import get_bytes
from snowdate.labels import first_snow_date, season_years_in
from snowdate.pack import DatePack
from snowdate.split import TRAIN, role


def _meta_for(sid: str, inventory: dict[str, dict[str, Any]], fallback_name: str) -> dict[str, Any]:
    rec = inventory.get(sid) or {}
    return {
        "station_id": sid,
        "name": rec.get("name") or fallback_name,
        "lat": float(rec.get("lat") or 0.0),
        "lon": float(rec.get("lon") or 0.0),
    }


def _rows_for_station(
    *,
    sid: str,
    name: str,
    lat: float,
    lon: float,
    days: list,
    floor: float = COMPLETE_FRAC,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    holes: dict[str, Any] = {"station_id": sid, "incomplete": [], "no_snow": []}
    rows: list[dict[str, Any]] = []
    for year in sorted(season_years_in(days)):
        obs, frac, reason = first_snow_date(days, year=int(year), floor=floor)
        if reason == "incomplete":
            holes["incomplete"].append({"target": FIRST_SNOW, "year": int(year), "complete_frac": frac})
            continue
        if reason == "no_snow_in_window":
            holes["no_snow"].append({"target": FIRST_SNOW, "year": int(year), "complete_frac": frac})
            continue
        rows.append(
            {
                "station_id": sid,
                "name": name,
                "lat": lat,
                "lon": lon,
                "target": FIRST_SNOW,
                "season_year": int(year),
                "obs_date": obs,
                "complete_frac": float(frac),
            }
        )
    return rows, holes


def _train_n(rows: list[dict[str, Any]]) -> int:
    return sum(1 for r in rows if role(r["target"], r["season_year"]) == TRAIN)


def fetch_live(*, cache_dir: Path, getter: Callable[[str], bytes] = get_bytes) -> tuple[DatePack, dict[str, Any]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    inventory = load_station_inventory(cache_dir, getter=getter)
    all_rows: list[dict[str, Any]] = []
    holes: list[dict[str, Any]] = []
    used_optional: str | None = None

    for sid, name in CORE_STATIONS:
        try:
            days = load_station_snow(sid, cache_dir, getter=getter)
        except FetchError:
            raise FetchError(f"empty GHCND SNOW for required core {sid}") from None
        meta = _meta_for(sid, inventory, name)
        rows, hole = _rows_for_station(sid=sid, name=meta["name"], lat=meta["lat"], lon=meta["lon"], days=days)
        n_train = _train_n(rows)
        if n_train < MIN_TRAIN_SEASONS:
            raise FetchError(f"core {sid} SNOW too thin for median: train n={n_train}")
        all_rows.extend(rows)
        holes.append(hole)

    holes.append({"station_id": MICHIGAN_CITY_ID, "dropped": True, "reason": "Michigan City stays out"})

    try:
        days = load_station_snow(VALPO_ID, cache_dir, getter=getter)
        meta = _meta_for(VALPO_ID, inventory, VALPO_NAME)
        rows, hole = _rows_for_station(sid=VALPO_ID, name=meta["name"], lat=meta["lat"], lon=meta["lon"], days=days)
        n_train = _train_n(rows)
        hole["train_n"] = n_train
        if n_train < MIN_TRAIN_SEASONS:
            hole["dropped"] = True
            hole["reason"] = "SNOW thin"
            holes.append(hole)
        else:
            all_rows.extend(rows)
            used_optional = VALPO_ID
            hole["dropped"] = False
            holes.append(hole)
    except FetchError as exc:
        holes.append({"station_id": VALPO_ID, "dropped": True, "reason": str(exc)})

    if not all_rows:
        raise FetchError("no complete station-winters after SNOW QC")
    missing_cores = set(CORE_IDS) - {r["station_id"] for r in all_rows}
    if missing_cores:
        raise FetchError(f"required cores missing after QC: {sorted(missing_cores)}")
    if any(r["station_id"] == MICHIGAN_CITY_ID for r in all_rows):
        raise FetchError("Michigan City leaked into the pack")

    pack = DatePack(
        station_id=np.array([r["station_id"] for r in all_rows], dtype=object),
        name=np.array([r["name"] for r in all_rows], dtype=object),
        lat=np.array([r["lat"] for r in all_rows], dtype=float),
        lon=np.array([r["lon"] for r in all_rows], dtype=float),
        target=np.array([r["target"] for r in all_rows], dtype=object),
        season_year=np.array([r["season_year"] for r in all_rows], dtype=int),
        obs_date=np.array([r["obs_date"] for r in all_rows], dtype=object),
        complete_frac=np.array([r["complete_frac"] for r in all_rows], dtype=float),
        source="live",
        extra={"used_optional": used_optional, "holes": holes, "element": "SNOW", "mc_in_core_mean": False},
    )
    meta = {
        "n_stations": pack.n_stations,
        "n_rows": pack.n_rows,
        "product": "GHCND SNOW",
        "units": "days",
        "snow_inch_min": 0.1,
        "used_optional": used_optional,
        "holes": holes,
        "cache_dir": str(cache_dir),
        "mc_in_core_mean": False,
    }
    return pack, meta
