# Copyright (c) 2026 Martial Systems LLC
"""80% SNOW completeness. Thin Valparaiso dropped. Michigan City not in the four-core mean."""

from __future__ import annotations

from typing import Any

from snowdateforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if not state.get("floor_ok"):
        v.append("floor")
    if state.get("thin_kept"):
        v.append("thin_kept")
    if state.get("optional_thin") and not state.get("optional_dropped"):
        v.append("optional_thin_kept")
    if state.get("mc_in_core_mean"):
        v.append("mc_in_core_mean")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="snowdate.completeness",
        evaluate=_evaluate,
        extra=["floor_ok", "thin_kept", "optional_thin", "optional_dropped", "mc_in_core_mean"],
    )
