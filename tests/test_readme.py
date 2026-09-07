# Copyright (c) 2026 Martial Systems LLC

from pathlib import Path

from snowdate.claims import scan_text
from snowdate.config import QUESTION

REPO = Path(__file__).resolve().parents[1]


def test_readme_opens_with_the_question() -> None:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    body = "\n".join(text.splitlines()[1:]).lstrip()
    assert body.startswith(QUESTION)
    assert body.splitlines()[2].startswith("No.")
    assert "1991-2020" in text
    assert "28941fb" in text
    assert "d861556" in text
    assert "9aa7935" in text
    assert "82ce0ce" in text
    assert "16.08" in text
    assert "24.58" in text
    assert "19.37" in text
    assert "31.61" in text
    assert "8.83" in text
    assert "13.00" in text
    assert "not a northern win" in text
    assert "not the method" in text
    assert "Pages stay off" in text
    assert "USW00014848" in text
    assert "USW00004846" in text
    assert "USC00125604" in text
    assert "The fixture is not the result" in text
    assert "logs/in_live/scatter.png" in text
    assert "logs/in_live/mae_bars.png" in text
    assert "Research index: https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3" in text
    assert "e5de316dbb5f672573906572730e3735" in text
    assert "Open_the_research_console" not in text
    assert scan_text(text) == []
    assert "\u2014" not in text
    assert "What it is not" not in text
    assert "frost outlook" not in text.lower()
    assert "Indiana will freeze on" not in text
    assert ".venv/bin/python -m pytest" in text
