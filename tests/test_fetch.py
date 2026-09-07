# Copyright (c) 2026 Martial Systems LLC

import gzip
from datetime import date
from pathlib import Path

import pytest

from snowdate.errors import FetchError
from snowdate.fetch import fetch_live
from snowdate.ghcnd import parse_snow_csv
from snowdate.labels import snow_mm_to_inches


def test_parse_snow_ignores_tmin_prcp_snwd() -> None:
    text = (
        "USW00014848,20181112,TMIN,0,,,\n"
        "USW00014848,20181112,PRCP,10,,,\n"
        "USW00014848,20181112,SNWD,50,,,\n"
        "USW00014848,20181112,SNOW,25,,,\n"
        "USW00014848,20181112,SNOW,-9999,,,\n"
    )
    rows = parse_snow_csv(text)
    assert rows == [(date(2018, 11, 12), snow_mm_to_inches(25))]
    assert snow_mm_to_inches(25) >= 0.1


def _gz(lines: list[str]) -> bytes:
    return gzip.compress("\n".join(lines).encode("utf-8"))


def test_empty_core_snow_stops(tmp_path: Path) -> None:
    def getter(url: str) -> bytes:
        if url.endswith("ghcnd-stations.txt"):
            return (
                "USW00014848  41.7100  -86.3200  236.0 SOUTH BEND          IN US\n"
                "USW00014827  41.1200  -85.1900  248.0 FORT WAYNE         IN US\n"
                "USW00093819  39.7200  -86.2900  241.0 INDIANAPOLIS       IN US\n"
                "USW00093817  38.0400  -87.5300  118.0 EVANSVILLE         IN US\n"
            ).encode()
        if "USW00014848" in url:
            return _gz(["USW00014848,20181112,TMIN,0,,,"])
        return _gz(["USW00014827,20181112,SNOW,25,,,"])

    with pytest.raises(FetchError, match="required core USW00014848"):
        fetch_live(cache_dir=tmp_path, getter=getter)
