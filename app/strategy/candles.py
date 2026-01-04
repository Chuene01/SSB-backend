import pandas as pd
from typing import Tuple


# =========
# Utilities
# =========

def candle_body(open_, close):
    return abs(close - open_)


def candle_range(high, low):
    return high - low


def closes_strongly_bullish(open_, close, high):
    return close > open_ and close >= high - (0.25 * (high - open_))


def closes_strongly_bearish(open_, close, low):
    return close < open_ and close <= low + (0.25 * (open_ - low))


def penetrates_zone(high, low, zone_low, zone_high) -> bool:
    return high >= zone_low and low <= zone_high


# =========
# Big Shadow (2-candle)
# =========

def is_big_shadow(df: pd.DataFrame, idx: int, direction: str) -> bool:
    """
    2-candle pattern.
    Candle 2 must engulf range expansion and close with intent.
    """
    if idx < 1:
        return False

    c1 = df.iloc[idx - 1]
    c2 = df.iloc[idx]

    range1 = candle_range(c1.high, c1.low)
    range2 = candle_range(c2.high, c2.low)

    # Must be largest of last 6 candles
    recent_ranges = [
        candle_range(df.iloc[i].high, df.iloc[i].low)
        for i in range(max(0, idx - 6), idx)
    ]

    if range2 <= max(recent_ranges, default=0):
        return False

    if direction == "bullish":
        return closes_strongly_bullish(c2.open, c2.close, c2.high)

    return closes_strongly_bearish(c2.open, c2.close, c2.low)


# =========
# Morning / Evening Star
# =========

def is_morning_star(df: pd.DataFrame, idx: int) -> bool:
    if idx < 2:
        return False

    c1 = df.iloc[idx - 2]
    c2 = df.iloc[idx - 1]
    c3 = df.iloc[idx]

    if c1.close >= c1.open:
        return False  # first must be bearish

    if candle_body(c2.open, c2.close) > candle_body(c1.open, c1.close) * 0.5:
        return False  # indecision candle too large

    mid_body = (c1.open + c1.close) / 2

    return c3.close > mid_body


def is_evening_star(df: pd.DataFrame, idx: int) -> bool:
    if idx < 2:
        return False

    c1 = df.iloc[idx - 2]
    c2 = df.iloc[idx - 1]
    c3 = df.iloc[idx]

    if c1.close <= c1.open:
        return False  # first must be bullish

    if candle_body(c2.open, c2.close) > candle_body(c1.open, c1.close) * 0.5:
        return False

    mid_body = (c1.open + c1.close) / 2

    return c3.close < mid_body


# =========
# FAILURE VALIDATION (used in Phase 2A)
# =========

def validate_failure_candle(
    df: pd.DataFrame,
    idx: int,
    direction: str,
    zone: Tuple[float, float],
) -> bool:
    """
    Confirms LH / HL after BOS.
    """
    candle = df.iloc[idx]
    zone_low, zone_high = zone

    if not penetrates_zone(candle.high, candle.low, zone_low, zone_high):
        return False

    if is_big_shadow(df, idx, direction):
        return True

    if direction == "bullish" and is_morning_star(df, idx):
        return True

    if direction == "bearish" and is_evening_star(df, idx):
        return True

    return False


# =========
# ENTRY VALIDATION (used after retest)
# =========

def validate_entry_candle(
    df: pd.DataFrame,
    idx: int,
    direction: str,
    zone: Tuple[float, float],
) -> bool:
    """
    Confirms entry on return into completed zone.
    """
    candle = df.iloc[idx]
    zone_low, zone_high = zone

    if not penetrates_zone(candle.high, candle.low, zone_low, zone_high):
        return False

    if is_big_shadow(df, idx, direction):
        return True

    if direction == "bullish" and is_morning_star(df, idx):
        return True

    if direction == "bearish" and is_evening_star(df, idx):
        return True

    return False
