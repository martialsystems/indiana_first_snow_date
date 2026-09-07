# Copyright (c) 2026 Martial Systems LLC
"""Pages snow-date hero refused until last year beats the median, or the README states the no."""

from __future__ import annotations

from typing import Any

from snowdateforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("page_in_scope") and not state.get("last_year_beats_median"):
        if not state.get("readme_states_no"):
            v.append("page_without_skill")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="snowdate.pages",
        evaluate=_evaluate,
        extra=["page_in_scope", "last_year_beats_median", "readme_states_no"],
    )
