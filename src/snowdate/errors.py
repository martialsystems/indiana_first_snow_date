# Copyright (c) 2026 Martial Systems LLC


class GateError(RuntimeError):
    """Stage hard gate failed."""


class ClaimBanError(GateError):
    """Report text hit a banned claim."""


class FetchError(GateError):
    """GHCND SNOW empty or thin for a required core, or a refused substitute."""


class SplitError(GateError):
    """Temporal split leaked confirmation into train or the median."""


class FigureCapError(GateError):
    """This tree stops at two figures."""


class CompletenessError(GateError):
    """A kept row is under the 80% SNOW floor."""
