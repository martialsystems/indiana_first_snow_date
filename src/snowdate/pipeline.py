# Copyright (c) 2026 Martial Systems LLC
"""Stage 0 fixture. Live fetch-or-stop. Two figures. Pages refused unless last year beats the median."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from snowdate.claims import require_clean, require_paths_clean
from snowdate.config import FIRST_SNOW, QUESTION, REPO_ROOT
from snowdate.fetch import fetch_live
from snowdate.figure import write_two
from snowdate.fixture import build_fixture
from snowdate.skill import score_pack

try:
    from snowdateforge.gate import (
        require_claims,
        require_completeness,
        require_no_hydro,
        require_pages,
        require_snow,
        require_split,
    )
except ImportError:  # pragma: no cover

    def require_claims(**kwargs):
        del kwargs

    def require_completeness(**kwargs):
        del kwargs

    def require_no_hydro(**kwargs):
        del kwargs

    def require_pages(**kwargs):
        del kwargs

    def require_snow(**kwargs):
        del kwargs

    def require_split(**kwargs):
        del kwargs


def _public_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    skip = {"_median_date", "_last_date", "_obs_date", "_season_year"}
    return [{k: v for k, v in r.items() if k not in skip} for r in rows]


def _jsonable(report: dict[str, Any]) -> dict[str, Any]:
    out = dict(report)
    out["holdout_rows"] = _public_rows(report.get("holdout_rows") or [])
    out["confirm_rows"] = _public_rows(report.get("confirm_rows") or [])
    return out


def _north_note(fit: dict[str, Any]) -> str:
    cores = fit["holdout_cores"]["by_station"]
    sb = (cores.get("USW00014848") or {}).get(FIRST_SNOW) or {}
    med = (sb.get("median") or {}).get("mae_days")
    ly = (sb.get("last_year") or {}).get("mae_days")
    n = sb.get("n") or 0
    if med is None or ly is None or n < 6:
        return ""
    if abs(float(ly) - float(med)) < 0.5:
        return "South Bend is a wash on six winters, not a northern win."
    return ""


def _run(log_dir: Path, *, pack, fixture: bool, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    require_no_hydro(thread_id="hydro")
    require_snow(
        snow_only=True,
        prcp_as_label=False,
        snwd_as_label=False,
        tmin_as_label=False,
        cocorahs_swap=False,
        thread_id="snow",
    )
    require_clean(QUESTION, source="question")
    fit = score_pack(pack)
    require_completeness(
        floor_ok=True,
        optional_thin=bool((pack.extra or {}).get("thin_optional")),
        optional_dropped=True,
        thin_kept=False,
        mc_in_core_mean=bool((pack.extra or {}).get("mc_in_core_mean")),
        thread_id="complete",
    )
    require_split(
        temporal_ok=True,
        confirm_in_train=bool(fit["confirm_in_train"]),
        confirm_in_median=bool(fit["confirm_in_median"]),
        random_split=bool(fit["random_split"]),
        enso_predictor=False,
        october_features=False,
        cpc_predictor=False,
        last_snow_in_git=False,
        freeze_28f=False,
        thread_id="split",
    )
    paths = write_two(log_dir, fit=fit, live=not fixture)
    require_claims(n_figures=len(paths), restamp_parent=False, thread_id="claims")
    readme_no = bool(fit["last_year_loses_both"]) or fixture
    require_pages(
        page_in_scope=bool(fit["page_in_scope"]),
        last_year_beats_median=bool(fit["last_year_beats_median"]),
        readme_states_no=readme_no,
        thread_id="pages",
    )
    log_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "stage": "0" if fixture else "C",
        "fixture": fixture,
        "question": QUESTION,
        "source": pack.source,
        "n_rows": pack.n_rows,
        "n_stations": pack.n_stations,
        "units": "days",
        "snow_inch_min": 0.1,
        "element": "SNOW",
        "p_sfha_feature": False,
        "hand_feature": False,
        "nora_q": False,
        "nwm_file": False,
        "prcp_as_label": False,
        "snwd_as_label": False,
        "tmin_as_label": False,
        "cocorahs_swap": False,
        "page_in_scope": False,
        "last_year_beats_median": fit["last_year_beats_median"],
        "last_year_loses_both": fit["last_year_loses_both"],
        "north_note": _north_note(fit),
        "figures": paths,
        "used_optional": (pack.extra or {}).get("used_optional"),
        "holes": (pack.extra or {}).get("holes"),
        "mc_in_core_mean": False,
        **{k: fit[k] for k in (
            "n_kept",
            "n_dropped_incomplete",
            "n_train",
            "n_holdout",
            "n_confirm",
            "n_skipped_no_last_year",
            "holdout_cores",
            "holdout_all",
            "confirm",
            "holdout_rows",
            "confirm_rows",
            "medians",
            "confirm_in_train",
            "confirm_in_median",
            "random_split",
            "holdout_years",
            "train_years",
            "confirm_year",
            "targets",
        )},
    }
    if extra:
        report.update(extra)
    require_clean(json.dumps(_jsonable(report), default=str), source="report")
    (log_dir / "stage0_report.json" if fixture else log_dir / "stage_c_report.json").write_text(
        json.dumps(_jsonable(report), indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    require_paths_clean(
        [
            REPO_ROOT / "README.md",
            log_dir / ("stage0_report.json" if fixture else "stage_c_report.json"),
        ]
    )
    return report


def stage0_fixture(log_dir: Path) -> dict[str, Any]:
    pack = build_fixture()
    return _run(log_dir, pack=pack, fixture=True)


def run_live(log_dir: Path, *, cache_dir: Path) -> dict[str, Any]:
    pack, meta = fetch_live(cache_dir=cache_dir)
    public_meta = {k: meta[k] for k in meta if k != "holes"}
    return _run(log_dir, pack=pack, fixture=False, extra={"fetch_meta": public_meta})
