"""Timestamp conversion utilities for Apple formats."""

from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional

# Epoch references
COCOA_EPOCH = datetime(2001, 1, 1)
UNIX_EPOCH = datetime(1970, 1, 1)
WEBKIT_EPOCH = datetime(1601, 1, 1)

# Cocoa to Unix offset (seconds)
COCOA_OFFSET = 978307200


def cocoa_to_datetime(ts: Optional[float]) -> Optional[datetime]:
    """Convert Cocoa/CoreData timestamp to datetime."""
    if not ts:
        return None
    try:
        if ts > 1e15:
            ts = ts / 1e9
        return COCOA_EPOCH + timedelta(seconds=ts)
    except (ValueError, OverflowError):
        return None


def unix_to_datetime(ts: Optional[float]) -> Optional[datetime]:
    """Convert Unix timestamp to datetime."""
    if not ts:
        return None
    try:
        if ts > 1e12:
            ts = ts / 1000
        return datetime.fromtimestamp(ts)
    except (ValueError, OverflowError, OSError):
        return None


def webkit_to_datetime(ts: Optional[float]) -> Optional[datetime]:
    """Convert WebKit timestamp (microseconds since 1601) to datetime."""
    if not ts:
        return None
    try:
        return WEBKIT_EPOCH + timedelta(microseconds=ts)
    except (ValueError, OverflowError):
        return None


def auto_convert(ts: Optional[float]) -> Optional[datetime]:
    """Auto-detect format and convert timestamp."""
    if not ts:
        return None
    
    if ts > 1e18:
        return cocoa_to_datetime(ts / 1e9)
    if ts > 1e16:
        return webkit_to_datetime(ts)
    if ts > 1e12:
        return unix_to_datetime(ts / 1000)
    if ts < 8e8:
        return cocoa_to_datetime(ts)
    return unix_to_datetime(ts)


def format_ts(dt: Optional[datetime], fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(fmt) if dt else ""
