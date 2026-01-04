from dataclasses import dataclass
from typing import List, Optional, Dict
import pandas as pd


# =========
# Data Models
# =========

@dataclass
class SwingPoint:
    index: int
    price: float


@dataclass
class StructureZone:
    direction: str              # "bullish" or "bearish"
    lower: float                # zone low
    upper: float                # zone high
    bos_index: int
    failure_index: int          # index of confirmed HL / LH
    timeframe: str


@dataclass
class StructureResult:
    valid: bool
    direction: Optional[str]    # "bullish" / "bearish" / None
    zone: Optional[StructureZone]
    reason: Optional[str]


# =========
# Swing Detection (Close-only, Line Chart)
# =========

def detect_swings(
    closes: pd.Series,
    lookback: int = 3
) -> Dict[str, List[SwingPoint]]:
    """
    Detect swing highs and lows using close price only.
    """
    highs: List[SwingPoint] = []
    lows: List[SwingPoint] = []

    for i in range(lookback, len(closes) - lookback):
        window = closes[i - lookback : i + lookback + 1]
        current = closes.iloc[i]

        if current == window.max():
            highs.append(SwingPoint(i, current))

        if current == window.min():
            lows.append(SwingPoint(i, current))

    return {"highs": highs, "lows": lows}


# =========
# Break of Structure (BOS)
# =========

def detect_bos(
    closes: pd.Series,
    swings: Dict[str, List[SwingPoint]]
) -> Optional[Dict]:
    """
    Detect the most recent valid BOS.
    """
    if not swings["highs"] or not swings["lows"]:
        return None

    last_close_index = len(closes) - 1
    last_close = closes.iloc[-1]

    last_hh = swings["highs"][-1]
    last_ll = swings["lows"][-1]

    if last_close > last_hh.price:
        return {
            "direction": "bullish",
            "level": last_hh,
            "index": last_close_index,
        }

    if last_close < last_ll.price:
        return {
            "direction": "bearish",
            "level": last_ll,
            "index": last_close_index,
        }

    return None


# =========
# Failure Detection (HL / LH confirmation)
# =========

def detect_failure(
    closes: pd.Series,
    bos: Dict,
    swings: Dict[str, List[SwingPoint]],
    failure_validator: callable,
) -> Optional[SwingPoint]:
    """
    Confirm HL / LH after BOS.
    failure_validator is a function from candles.py
    """

    direction = bos["direction"]
    bos_level = bos["level"]

    if direction == "bullish":
        # HL must be AFTER BOS and ABOVE broken HH
        for low in reversed(swings["lows"]):
            if low.index > bos["index"] and low.price > bos_level.price:
                if failure_validator(low.index):
                    return low

    if direction == "bearish":
        # LH must be AFTER BOS and BELOW broken LL
        for high in reversed(swings["highs"]):
            if high.index > bos["index"] and high.price < bos_level.price:
                if failure_validator(high.index):
                    return high

    return None


# =========
# Structure Zone Construction
# =========

def build_zone(
    direction: str,
    bos_level: SwingPoint,
    failure_point: SwingPoint,
    timeframe: str,
    bos_index: int,
) -> StructureZone:
    """
    Zones are completed at failure confirmation.
    """

    if direction == "bullish":
        lower = failure_point.price
        upper = bos_level.price

    else:  # bearish
        lower = bos_level.price
        upper = failure_point.price

    return StructureZone(
        direction=direction,
        lower=min(lower, upper),
        upper=max(lower, upper),
        bos_index=bos_index,
        failure_index=failure_point.index,
        timeframe=timeframe,
    )


# =========
# Full Structure Evaluation (Single Timeframe)
# =========

def evaluate_structure(
    df: pd.DataFrame,
    timeframe: str,
    failure_validator: callable,
) -> StructureResult:
    """
    Evaluate full structure on ONE timeframe.
    """

    closes = df["close"]

    swings = detect_swings(closes)
    bos = detect_bos(closes, swings)

    if not bos:
        return StructureResult(False, None, None, "No BOS")

    failure_point = detect_failure(
        closes=closes,
        bos=bos,
        swings=swings,
        failure_validator=failure_validator,
    )

    if not failure_point:
        return StructureResult(False, None, None, "No failure confirmation")

    zone = build_zone(
        direction=bos["direction"],
        bos_level=bos["level"],
        failure_point=failure_point,
        timeframe=timeframe,
        bos_index=bos["index"],
    )

    return StructureResult(
        valid=True,
        direction=bos["direction"],
        zone=zone,
        reason=None,
    )
