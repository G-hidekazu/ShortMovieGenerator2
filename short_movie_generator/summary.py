"""Utility helpers for presenting transcript information."""
from __future__ import annotations

import math


def format_timestamp(seconds: float) -> str:
    """Format seconds into a mm:ss timestamp for display."""

    minutes = int(seconds // 60)
    secs = int(math.floor(seconds % 60))
    return f"{minutes:02d}:{secs:02d}"
