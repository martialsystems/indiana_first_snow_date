# Copyright (c) 2026 Martial Systems LLC
"""Temporal split. Confirmation 2025-26 is out of train and out of the median."""

from __future__ import annotations

from snowdate.config import CONFIRM_YEAR, FIRST_SNOW, HOLDOUT_YEARS, TRAIN_YEARS
from snowdate.errors import SplitError

TRAIN = "train"
HOLDOUT = "holdout"
CONFIRM = "confirm"
OTHER = "other"


def role(target: str, year: int) -> str:
    if target != FIRST_SNOW:
        raise SplitError(f"unknown target {target}")
    y = int(year)
    if y in TRAIN_YEARS:
        return TRAIN
    if y in HOLDOUT_YEARS:
        return HOLDOUT
    if y == CONFIRM_YEAR:
        return CONFIRM
    return OTHER


def assert_split(*, confirm_in_train: bool, confirm_in_median: bool, random_split: bool) -> None:
    if confirm_in_train or confirm_in_median:
        raise SplitError("confirmation leaked into train or the median")
    if random_split:
        raise SplitError("random row split is refused")
