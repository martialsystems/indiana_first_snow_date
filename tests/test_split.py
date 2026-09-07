# Copyright (c) 2026 Martial Systems LLC

import pytest

from snowdate.errors import SplitError
from snowdate.split import CONFIRM, HOLDOUT, TRAIN, assert_split, role


def test_pinned_years() -> None:
    assert role("first_snow", 2018) == TRAIN
    assert role("first_snow", 2019) == HOLDOUT
    assert role("first_snow", 2024) == HOLDOUT
    assert role("first_snow", 2025) == CONFIRM
    assert role("first_snow", 1991) == TRAIN


def test_confirm_leak_refused() -> None:
    with pytest.raises(SplitError):
        assert_split(confirm_in_train=True, confirm_in_median=False, random_split=False)
    with pytest.raises(SplitError):
        assert_split(confirm_in_train=False, confirm_in_median=True, random_split=False)
