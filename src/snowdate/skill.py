# Copyright (c) 2026 Martial Systems LLC
"""Median (train-era 1991-2020) vs last year. MAE in days leads."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

import numpy as np

from snowdate.config import (
    CLIMATE_FIRST,
    CLIMATE_LAST,
    COMPLETE_FRAC,
    CORE_IDS,
    FIRST_SNOW,
    HOLDOUT_YEARS,
    TARGETS,
    TRAIN_YEARS,
)
from snowdate.dates import date_from_season_doy, error_days, iso, month_day, season_doy
from snowdate.pack import DatePack
from snowdate.split import CONFIRM, HOLDOUT, TRAIN, assert_split, role


def _keep_complete(pack: DatePack) -> np.ndarray:
    return np.asarray(pack.complete_frac, dtype=float) >= COMPLETE_FRAC


def _median_dates(pack: DatePack, keep: np.ndarray) -> dict[tuple[str, str], date]:
    buckets: dict[tuple[str, str], list[int]] = defaultdict(list)
    for i in np.flatnonzero(keep):
        sid = str(pack.station_id[i])
        tgt = str(pack.target[i])
        year = int(pack.season_year[i])
        if role(tgt, year) != TRAIN:
            continue
        if year < CLIMATE_FIRST or year > CLIMATE_LAST:
            continue
        buckets[(sid, tgt)].append(season_doy(pack.obs_date[i], year))
    out: dict[tuple[str, str], date] = {}
    for key, vals in buckets.items():
        if not vals:
            continue
        # Map median season-doy onto a non-leap climate year for month-day print.
        out[key] = date_from_season_doy(float(np.median(np.asarray(vals, dtype=float))), 1999)
    return out


def _lookup(pack: DatePack, keep: np.ndarray) -> dict[tuple[str, str, int], date]:
    out: dict[tuple[str, str, int], date] = {}
    for i in np.flatnonzero(keep):
        out[(str(pack.station_id[i]), str(pack.target[i]), int(pack.season_year[i]))] = pack.obs_date[i]
    return out


def _stats(err: list[int]) -> dict[str, float]:
    a = np.asarray(err, dtype=float)
    if a.size == 0:
        return {"n": 0, "mae_days": float("nan"), "rmse_days": float("nan"), "bias_days": float("nan")}
    return {
        "n": int(a.size),
        "mae_days": float(np.mean(np.abs(a))),
        "rmse_days": float(np.sqrt(np.mean(a * a))),
        "bias_days": float(np.mean(a)),
    }


def _row_payload(
    *,
    pack: DatePack,
    i: int,
    median: date,
    last: date,
    split: str,
) -> dict[str, Any]:
    obs = pack.obs_date[i]
    year = int(pack.season_year[i])
    last_year = int(pack.season_year[i]) - 1
    med_on_year = date_from_season_doy(season_doy(median, 1999), year)
    last_on_year = date_from_season_doy(season_doy(last, last_year), year)
    e_med = error_days(med_on_year, obs, year)
    e_ly = error_days(last_on_year, obs, year)
    return {
        "station_id": str(pack.station_id[i]),
        "name": str(pack.name[i]),
        "lat": float(pack.lat[i]),
        "lon": float(pack.lon[i]),
        "target": str(pack.target[i]),
        "season_year": year,
        "split": split,
        "obs": iso(obs),
        "obs_season_doy": season_doy(obs, year),
        "median": month_day(median),
        "median_season_doy": season_doy(median, 1999),
        "last_year": iso(last),
        "last_year_season_doy": season_doy(last, last_year),
        "err_median_days": int(e_med),
        "err_last_year_days": int(e_ly),
        "last_year_beats_median": abs(e_ly) < abs(e_med),
        "complete_frac": float(pack.complete_frac[i]),
        "_median_date": med_on_year,
        "_last_date": last_on_year,
        "_obs_date": obs,
        "_season_year": year,
    }


def score_pack(pack: DatePack) -> dict[str, Any]:
    keep = _keep_complete(pack)
    dropped = int((~keep).sum())
    medians = _median_dates(pack, keep)
    lookup = _lookup(pack, keep)
    assert_split(confirm_in_train=False, confirm_in_median=False, random_split=False)

    hold_rows: list[dict[str, Any]] = []
    conf_rows: list[dict[str, Any]] = []
    skipped_no_last: list[dict[str, Any]] = []
    for i in np.flatnonzero(keep):
        sid = str(pack.station_id[i])
        tgt = str(pack.target[i])
        year = int(pack.season_year[i])
        r = role(tgt, year)
        if r not in {HOLDOUT, CONFIRM}:
            continue
        med = medians.get((sid, tgt))
        last = lookup.get((sid, tgt, year - 1))
        if med is None:
            continue
        if last is None:
            skipped_no_last.append({"station_id": sid, "target": tgt, "season_year": year, "split": r})
            continue
        payload = _row_payload(pack=pack, i=i, median=med, last=last, split=r)
        if r == HOLDOUT:
            hold_rows.append(payload)
        else:
            conf_rows.append(payload)

    def _block(rows: list[dict[str, Any]], *, cores_only: bool) -> dict[str, Any]:
        use = [x for x in rows if (x["station_id"] in CORE_IDS) or not cores_only]
        by_tgt: dict[str, dict[str, Any]] = {}
        for tgt in TARGETS:
            sub = [x for x in use if x["target"] == tgt]
            by_tgt[tgt] = {
                "median": _stats([x["err_median_days"] for x in sub]),
                "last_year": _stats([x["err_last_year_days"] for x in sub]),
                "n_last_year_beats": int(sum(1 for x in sub if x["last_year_beats_median"])),
                "n": len(sub),
            }
        by_st: dict[str, dict[str, Any]] = {}
        for sid in sorted({x["station_id"] for x in use}):
            name = next(x["name"] for x in use if x["station_id"] == sid)
            cell: dict[str, Any] = {"name": name, "station_id": sid}
            for tgt in TARGETS:
                sub = [x for x in use if x["station_id"] == sid and x["target"] == tgt]
                cell[tgt] = {
                    "median": _stats([x["err_median_days"] for x in sub]),
                    "last_year": _stats([x["err_last_year_days"] for x in sub]),
                    "n_last_year_beats": int(sum(1 for x in sub if x["last_year_beats_median"])),
                    "n": len(sub),
                }
            by_st[sid] = cell
        scored = [t for t in TARGETS if by_tgt[t]["n"]]
        last_year_beats = bool(scored) and all(
            by_tgt[t]["last_year"]["mae_days"] < by_tgt[t]["median"]["mae_days"] for t in scored
        )
        last_year_loses = bool(scored) and all(
            by_tgt[t]["last_year"]["mae_days"] >= by_tgt[t]["median"]["mae_days"] for t in scored
        )
        return {
            "by_target": by_tgt,
            "by_station": by_st,
            "last_year_beats_both": last_year_beats,
            "last_year_loses_both": last_year_loses,
            "n": len(use),
        }

    cores = _block(hold_rows, cores_only=True)
    all_st = _block(hold_rows, cores_only=False)
    n_train = int(sum(1 for i in np.flatnonzero(keep) if role(str(pack.target[i]), int(pack.season_year[i])) == TRAIN))
    return {
        "n_rows": pack.n_rows,
        "n_kept": int(keep.sum()),
        "n_dropped_incomplete": dropped,
        "n_train": n_train,
        "n_holdout": len(hold_rows),
        "n_confirm": len(conf_rows),
        "n_skipped_no_last_year": len(skipped_no_last),
        "skipped_no_last_year": skipped_no_last,
        "holdout_cores": cores,
        "holdout_all": all_st,
        "confirm": _block(conf_rows, cores_only=True) if conf_rows else None,
        "holdout_rows": hold_rows,
        "confirm_rows": conf_rows,
        "medians": {f"{k[0]}|{k[1]}": month_day(v) for k, v in medians.items()},
        "confirm_in_train": False,
        "confirm_in_median": False,
        "random_split": False,
        "last_year_beats_median": bool(cores["last_year_beats_both"]),
        "last_year_loses_both": bool(cores["last_year_loses_both"]),
        "page_in_scope": False,
        "units": "days",
        "snow_inch_min": 0.1,
        "element": "SNOW",
        "holdout_years": list(HOLDOUT_YEARS),
        "train_years": f"{TRAIN_YEARS[0]}-{TRAIN_YEARS[-1]}",
        "confirm_year": 2025,
        "targets": [FIRST_SNOW],
    }
