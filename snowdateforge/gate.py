# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from typing import Any

from snowdateforge._bootstrap import ensure_paths

ensure_paths()

from graphforge.product_law import require_law

from snowdateforge.graphs.claim_bans import build_graph as build_claims
from snowdateforge.graphs.completeness import build_graph as build_complete
from snowdateforge.graphs.no_hydro import build_graph as build_hydro
from snowdateforge.graphs.pages import build_graph as build_pages
from snowdateforge.graphs.snow_only import build_graph as build_snow
from snowdateforge.graphs.temporal_split import build_graph as build_split


def require_no_hydro(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "snowdate_hydro"))
    state = {
        "p_sfha_feature": False,
        "p_sfha_label": False,
        "hand_feature": False,
        "nora_q": False,
        "nwm_file": False,
    }
    state.update(flags)
    require_law(build_hydro(), state, allow_decisions=["allow"], law_id="snowdate.no_hydro", thread_id=thread_id, raise_error=True)


def require_snow(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "snowdate_snow"))
    state = {
        "snow_only": False,
        "prcp_as_label": False,
        "snwd_as_label": False,
        "tmin_as_label": False,
        "cocorahs_swap": False,
    }
    state.update(flags)
    require_law(build_snow(), state, allow_decisions=["allow"], law_id="snowdate.snow_only", thread_id=thread_id, raise_error=True)


def require_completeness(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "snowdate_complete"))
    state = {
        "floor_ok": False,
        "thin_kept": False,
        "optional_thin": False,
        "optional_dropped": False,
        "mc_in_core_mean": False,
    }
    state.update(flags)
    require_law(
        build_complete(),
        state,
        allow_decisions=["allow"],
        law_id="snowdate.completeness",
        thread_id=thread_id,
        raise_error=True,
    )


def require_split(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "snowdate_split"))
    state = {
        "temporal_ok": True,
        "confirm_in_train": False,
        "confirm_in_median": False,
        "random_split": False,
        "enso_predictor": False,
        "october_features": False,
        "cpc_predictor": False,
        "last_snow_in_git": False,
        "freeze_28f": False,
    }
    state.update(flags)
    require_law(
        build_split(),
        state,
        allow_decisions=["allow"],
        law_id="snowdate.temporal_split",
        thread_id=thread_id,
        raise_error=True,
    )


def require_claims(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "snowdate_claims"))
    state = {
        "frost_warning": False,
        "will_get_inches": False,
        "flood": False,
        "p_sfha": False,
        "casualty": False,
        "restamp_parent": False,
        "n_figures": 2,
    }
    state.update(flags)
    require_law(
        build_claims(),
        state,
        allow_decisions=["allow"],
        law_id="snowdate.claim_bans",
        thread_id=thread_id,
        raise_error=True,
    )


def require_pages(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "snowdate_pages"))
    state = {
        "page_in_scope": False,
        "last_year_beats_median": False,
        "readme_states_no": False,
    }
    state.update(flags)
    require_law(build_pages(), state, allow_decisions=["allow"], law_id="snowdate.pages", thread_id=thread_id, raise_error=True)
