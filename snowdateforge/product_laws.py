# Copyright (c) 2026 Martial Systems LLC
"""Refuse laws. Verify-before-done is the finish gate."""

from __future__ import annotations

from typing import Any


def laws() -> list[dict[str, Any]]:
    from snowdateforge.graphs.claim_bans import build_graph as claim_bans
    from snowdateforge.graphs.completeness import build_graph as completeness
    from snowdateforge.graphs.no_hydro import build_graph as no_hydro
    from snowdateforge.graphs.pages import build_graph as pages
    from snowdateforge.graphs.snow_only import build_graph as snow_only
    from snowdateforge.graphs.temporal_split import build_graph as temporal_split

    return [
        {
            "id": "snowdate.no_hydro",
            "build": no_hydro,
            "state": {
                "p_sfha_feature": False,
                "p_sfha_label": False,
                "hand_feature": False,
                "nora_q": False,
                "nwm_file": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "snowdate.snow_only",
            "build": snow_only,
            "state": {
                "snow_only": True,
                "prcp_as_label": False,
                "snwd_as_label": False,
                "tmin_as_label": False,
                "cocorahs_swap": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "snowdate.completeness",
            "build": completeness,
            "state": {
                "floor_ok": True,
                "thin_kept": False,
                "optional_thin": False,
                "optional_dropped": True,
                "mc_in_core_mean": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "snowdate.temporal_split",
            "build": temporal_split,
            "state": {
                "temporal_ok": True,
                "confirm_in_train": False,
                "confirm_in_median": False,
                "random_split": False,
                "enso_predictor": False,
                "october_features": False,
                "cpc_predictor": False,
                "last_snow_in_git": False,
                "freeze_28f": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "snowdate.claim_bans",
            "build": claim_bans,
            "state": {
                "frost_warning": False,
                "will_get_inches": False,
                "flood": False,
                "p_sfha": False,
                "casualty": False,
                "restamp_parent": False,
                "n_figures": 2,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "snowdate.pages",
            "build": pages,
            "state": {
                "page_in_scope": False,
                "last_year_beats_median": False,
                "readme_states_no": True,
            },
            "allow_decisions": ["allow"],
        },
    ]
