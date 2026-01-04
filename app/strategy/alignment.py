from typing import Dict, Optional
from app.strategy.structure import StructureResult


def evaluate_alignment(
    structure_results: Dict[str, StructureResult],
) -> Dict:
    """
    Apply 2-of-3 timeframe alignment rule.

    Returns:
        {
            "aligned": bool,
            "direction": "bullish" | "bearish" | None,
            "valid_timeframes": [tf, tf],
            "reason": str | None
        }
    """

    bullish_tfs = []
    bearish_tfs = []

    for tf, result in structure_results.items():
        if not result.valid:
            continue

        if result.direction == "bullish":
            bullish_tfs.append(tf)

        elif result.direction == "bearish":
            bearish_tfs.append(tf)

    if len(bullish_tfs) >= 2:
        return {
            "aligned": True,
            "direction": "bullish",
            "valid_timeframes": bullish_tfs,
            "reason": None,
        }

    if len(bearish_tfs) >= 2:
        return {
            "aligned": True,
            "direction": "bearish",
            "valid_timeframes": bearish_tfs,
            "reason": None,
        }

    return {
        "aligned": False,
        "direction": None,
        "valid_timeframes": [],
        "reason": "Less than 2 timeframes aligned",
    }
