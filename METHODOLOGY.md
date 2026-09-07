# Methodology: first 0.1 in SNOW date vs 1991-2020 median

Question: Does last year's first 0.1 in GHCND SNOW date beat the 1991-2020 median date at held-out Indiana GHCND cores?

## Label

GHCND `SNOW` in mm, converted to inches. First date in the snow-year window with SNOW ≥ 0.1 in. Day-of-year from 1 July. Not SNWD. Not liquid PRCP. Not TMIN.

| Target | Rule | Season year |
|--------|------|-------------|
| First 0.1 in SNOW | First day with SNOW ≥ 0.1 in on 1 July Y through 30 June Y+1 | Y for winter Y/Y+1 |

Missing SNOW: drop that station-winter if completeness is under 80% of days in the window. No measurable snow in the window is also a drop. Empty SNOW for a required core stops.

Skill uses season day-of-year from 1 July so last year is a seasonal lag. Printed dates are the real calendar dates.

## Stations

Required cores: South Bend `USW00014848`, Fort Wayne `USW00014827`, Indianapolis `USW00093819`, Evansville `USW00093817`.

Optional fifth: Valparaiso `USW00004846` if SNOW clears the 80% floor and the train floor. Extra row, not averaged into the four-core lead. Michigan City `USC00125604` stays out.

## Bars

Bar A: 1991-2020 median first-snow date at that station, computed on train-era winters only (1991-2018). Holdout and confirmation do not set the median.

Bar B: last year's first-snow date at that station. A holdout row is scored only when last year is also complete.

No October Niño, October TAVG, October PRCP, ENSO, or CPC in this tree.

## Split

Rows: station × winter.

Train: winters 1991-92 through 2018-19 (season year 1991-2018).

Holdout: winters 2019-20 through 2024-25 (season year 2019-2024). Four cores complete: n=24 station-winters.

Confirmation: winter 2025-26 (season year 2025), out of train and out of the median.

## Metrics

Lead with MAE in days vs the median. RMSE second. Per-station table required. Counts of winters where last year wins a row are not the method.

## Figures

1. Holdout scatter: predicted vs observed season day-of-year, 1:1, median vs last year.
2. Per-station MAE bars: median vs last year. Caption: days of error, not a frost warning.

## Parents

Cite freeze `28941fb`, ENSO-freeze `d861556`, DJF snow `9aa7935`, NWI lake snow `82ce0ce`. Do not restamp them. Live skill is in `logs/in_live/stage_c_report.json`. Last year does not beat the median on holdout MAE or RMSE. Pages stay off.
