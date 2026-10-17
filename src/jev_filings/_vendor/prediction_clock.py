"""``PredictionClock``, copied verbatim from MCI-GRU's ``mci_gru/data/pit.py``.

Only this class and the regex it checks against are vendored; the rest of that
module (point-in-time universe masks) needs PyTorch and is not used here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd

_CLOCK_TIME = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


@dataclass(frozen=True)
class PredictionClock:
    """The time of day, in one timezone, at which the forecast for date D is made.

    Production is 20:00 America/New_York (#225 ruling 1); a fixture may declare its own.
    """

    time: str = "20:00"
    timezone: str = "America/New_York"

    def __post_init__(self) -> None:
        if not _CLOCK_TIME.match(str(self.time)):
            raise ValueError(f"prediction clock time must be HH:MM, got {self.time!r}")
        try:
            pd.Timestamp("2000-01-03").tz_localize(self.timezone)
        except Exception as exc:
            raise ValueError(f"unknown prediction clock timezone {self.timezone!r}") from exc

    def at(self, date: str) -> pd.Timestamp:
        """UTC instant of the forecast for ``date``."""
        local = pd.Timestamp(f"{date}T{self.time}:00").tz_localize(
            self.timezone, ambiguous="raise", nonexistent="raise"
        )
        return local.tz_convert("UTC")

    def to_dict(self) -> dict[str, str]:
        return {"time": self.time, "timezone": self.timezone}

