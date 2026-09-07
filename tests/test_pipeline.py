# Copyright (c) 2026 Martial Systems LLC

from pathlib import Path

from snowdate.config import QUESTION
from snowdate.errors import FigureCapError
from snowdate.figure import _cap
from snowdate.pipeline import stage0_fixture


def test_fixture_two_figures(tmp_path: Path) -> None:
    report = stage0_fixture(tmp_path)
    assert report["question"] == QUESTION
    assert report["figures"] == ["scatter.png", "mae_bars.png"]
    assert (tmp_path / "scatter.png").is_file()
    assert (tmp_path / "mae_bars.png").is_file()
    assert report["p_sfha_feature"] is False
    assert report["nwm_file"] is False
    assert report["prcp_as_label"] is False
    assert report["tmin_as_label"] is False
    assert report["page_in_scope"] is False
    assert report["element"] == "SNOW"
    assert report["n_dropped_incomplete"] >= 1
    cores = report["holdout_cores"]["by_station"]
    assert "USW00014848" in cores
    assert "USW00093817" in cores
    assert "USW00004846" not in cores
    assert "USC00125604" not in cores
    by_tgt = report["holdout_cores"]["by_target"]
    assert by_tgt["first_snow"]["n"] > 0
    assert report["confirm_in_train"] is False
    assert report["confirm_in_median"] is False
    assert report["holdout_years"] == [2019, 2020, 2021, 2022, 2023, 2024]


def test_live_holdout_keeps_page_closed() -> None:
    import json

    path = Path(__file__).resolve().parents[1] / "logs" / "in_live" / "stage_c_report.json"
    live = json.loads(path.read_text(encoding="utf-8"))
    assert live["page_in_scope"] is False
    assert live["element"] == "SNOW"
    assert live["mc_in_core_mean"] is False
    assert live["last_year_beats_median"] is False
    assert live["last_year_loses_both"] is True
    assert live["used_optional"] is None
    snow = live["holdout_cores"]["by_target"]["first_snow"]
    assert snow["n"] == 24
    assert snow["last_year"]["mae_days"] > snow["median"]["mae_days"]
    assert snow["last_year"]["rmse_days"] > snow["median"]["rmse_days"]
    assert abs(snow["median"]["mae_days"] - 16.08) < 0.01
    assert abs(snow["last_year"]["mae_days"] - 24.58) < 0.01
    assert "USW00014848" in live["holdout_cores"]["by_station"]
    assert "USW00004846" not in live["holdout_cores"]["by_station"]
    assert "USC00125604" not in live["holdout_cores"]["by_station"]
    assert live["confirm_in_median"] is False
    sb = live["holdout_cores"]["by_station"]["USW00014848"]["first_snow"]
    assert sb["last_year"]["mae_days"] > sb["median"]["mae_days"]


def test_bar_labels_are_city_names_and_do_not_overlap() -> None:
    import json

    from snowdate.config import CORE_STATIONS, LIVE_BARS_SUBTITLE
    from snowdate.figure import bar_station_labels, draw_bars

    live = Path(__file__).resolve().parents[1] / "logs" / "in_live" / "stage_c_report.json"
    fit = json.loads(live.read_text(encoding="utf-8"))
    order, labels = bar_station_labels(fit["holdout_cores"]["by_station"])
    cities = [name for sid, name in CORE_STATIONS if sid in order]
    assert labels == cities
    assert labels == ["South Bend", "Fort Wayne", "Indianapolis", "Evansville"]
    assert "INTL AP" not in " ".join(labels)
    assert "S BEND" not in " ".join(labels)
    fig = draw_bars(fit, title="Per-station holdout MAE", subtitle=LIVE_BARS_SUBTITLE)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for ax in fig.axes:
        boxes = [t.get_window_extent(renderer=renderer) for t in ax.get_xticklabels()]
        assert len(boxes) == 4
        for left, right in zip(boxes, boxes[1:]):
            assert not left.overlaps(right), (left, right)
    import matplotlib.pyplot as plt

    plt.close(fig)


def test_third_figure_refused() -> None:
    try:
        _cap(3)
        raise AssertionError("cap allowed 3")
    except FigureCapError:
        pass
