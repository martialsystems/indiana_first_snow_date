# Copyright (c) 2026 Martial Systems LLC
"""SNOW 0.1 in is the label. PRCP, SNWD, TMIN, and CoCoRaHS cannot substitute."""

from __future__ import annotations

from typing import Any

from snowdateforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if not state.get("snow_only"):
        v.append("not_snow")
    if state.get("prcp_as_label"):
        v.append("prcp_as_label")
    if state.get("snwd_as_label"):
        v.append("snwd_as_label")
    if state.get("tmin_as_label"):
        v.append("tmin_as_label")
    if state.get("cocorahs_swap"):
        v.append("cocorahs_swap")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="snowdate.snow_only",
        evaluate=_evaluate,
        extra=["snow_only", "prcp_as_label", "snwd_as_label", "tmin_as_label", "cocorahs_swap"],
    )
