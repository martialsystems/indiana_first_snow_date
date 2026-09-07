# Copyright (c) 2026 Martial Systems LLC

import pytest

from snowdate.claims import require_clean, scan_text
from snowdate.config import QUESTION
from snowdate.errors import ClaimBanError


def test_allowed_and_banned() -> None:
    assert scan_text(QUESTION) == []
    assert scan_text("days of error, not a frost warning.") == []
    assert "frost_warning" in scan_text("a frost warning is in effect")
    assert "will_get_inches" in scan_text("will get 12 inches")
    assert "flood_warning" in scan_text("flood warning tonight")
    assert "p_sfha" in scan_text("p_sfha as a snow date")
    with pytest.raises(ClaimBanError):
        require_clean("Indiana will freeze on 2026-10-12", source="t")
