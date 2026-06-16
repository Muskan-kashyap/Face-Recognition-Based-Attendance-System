"""
Pure business rules for attendance decisioning.

This module must remain dependency-free so it can be safely unit-tested
and reused by multiple pipelines/adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, date, time
from typing import Iterable, Optional, Tuple


@dataclass(frozen=True)
class ShiftRules:
    start_time: time
    end_time: time
    grace_period_mins: int
    buffer_mins: int


def compute_shift_status(
    *,
    shift: ShiftRules,
    timestamp: datetime,
) -> str:
    """
    Decide status based on shift start + grace and buffer.

    Returns one of:
    - on_time
    - late
    - early
    - absent
    """
    # NOTE: Current system uses "today" timestamps; production should supply
    # date context explicitly. Keeping pure rule here to match existing usage.
    shift_date: date = timestamp.date()
    dt_start = datetime.combine(shift_date, shift.start_time)
    dt_check = timestamp

    diff_mins = (dt_check - dt_start).total_seconds() / 60.0

    if diff_mins > shift.grace_period_mins:
        return "late"
    if diff_mins < -shift.buffer_mins:
        return "early"

    # absent is generally handled by "no check-in exists" logic, which is
    # outside this function's responsibility.
    return "on_time"


def apply_dedupe_rules(
    *,
    existing_logs: Iterable[datetime],
    proposed_check_in: datetime,
    dedupe_window_mins: int = 30,
) -> Tuple[datetime, bool]:
    """
    Decide whether proposed_check_in should be accepted or treated as duplicate.

    Returns (final_check_in, is_duplicate).

    Dedupe strategy:
    - if any existing log occurs within dedupe_window_mins of proposed_check_in,
      treat as duplicate (return proposed_check_in unchanged, is_duplicate=True)

    This mirrors typical "one attendance per window" semantics.
    """
    for prev in existing_logs:
        delta_mins = abs((proposed_check_in - prev).total_seconds() / 60.0)
        if delta_mins <= dedupe_window_mins:
            return proposed_check_in, True

    return proposed_check_in, False
