# Copyright (c) 2026 Martial Systems LLC

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from snowdateforge._bootstrap import ensure_paths

ensure_paths()

from graphforge.product_law import LawBlockedError

from snowdateforge.gate import (
    require_claims,
    require_completeness,
    require_no_hydro,
    require_pages,
    require_snow,
    require_split,
)
from snowdateforge.product_laws import laws


def test_laws() -> None:
    require_no_hydro(thread_id="t.h.ok")
    with pytest.raises(LawBlockedError):
        require_no_hydro(p_sfha_feature=True, thread_id="t.h.p")
    require_snow(snow_only=True, thread_id="t.s.ok")
    with pytest.raises(LawBlockedError):
        require_snow(snow_only=True, prcp_as_label=True, thread_id="t.s.prcp")
    with pytest.raises(LawBlockedError):
        require_snow(snow_only=True, tmin_as_label=True, thread_id="t.s.tmin")
    require_completeness(floor_ok=True, optional_thin=True, optional_dropped=True, thread_id="t.c.ok")
    with pytest.raises(LawBlockedError):
        require_completeness(floor_ok=True, mc_in_core_mean=True, thread_id="t.c.mc")
    require_split(thread_id="t.t.ok")
    with pytest.raises(LawBlockedError):
        require_split(enso_predictor=True, thread_id="t.t.enso")
    with pytest.raises(LawBlockedError):
        require_split(freeze_28f=True, thread_id="t.t.28")
    require_claims(n_figures=2, thread_id="t.k.ok")
    with pytest.raises(LawBlockedError):
        require_claims(n_figures=3, thread_id="t.k.fig")
    require_pages(page_in_scope=False, readme_states_no=True, thread_id="t.p.ok")
    with pytest.raises(LawBlockedError):
        require_pages(page_in_scope=True, last_year_beats_median=False, readme_states_no=False, thread_id="t.p.bad")
    assert {row["id"] for row in laws()} == {
        "snowdate.no_hydro",
        "snowdate.snow_only",
        "snowdate.completeness",
        "snowdate.temporal_split",
        "snowdate.claim_bans",
        "snowdate.pages",
    }
