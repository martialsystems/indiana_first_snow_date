# Copyright (c) 2026 Martial Systems LLC
from __future__ import annotations

from typing import Any

from snowdateforge.graphs._common import binary_graph

_BAD = (
    "confirm_in_train",
    "confirm_in_median",
    "random_split",
    "enso_predictor",
    "october_features",
    "cpc_predictor",
    "last_snow_in_git",
    "freeze_28f",
)


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if not state.get("temporal_ok"):
        v.append("not_temporal")
    for k in _BAD:
        if state.get(k):
            v.append(k)
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="snowdate.temporal_split",
        evaluate=_evaluate,
        extra=["temporal_ok", *_BAD],
    )
