from typing import Dict


def usd_position(symbol: str) -> str:
    """
    Determine whether USD is BASE or QUOTE currency.
    """
    if symbol.startswith("USD"):
        return "base"
    if symbol.endswith("USD"):
        return "quote"
    raise ValueError(f"Unsupported symbol for USD logic: {symbol}")


def implied_usd_bias(
    pair_direction: str,
    usd_pos: str,
) -> str:
    """
    Determine implied USD strength or weakness.
    """
    if usd_pos == "quote":
        # EURUSD ↑ = USD weak
        return "weak" if pair_direction == "bullish" else "strong"

    # usd_pos == "base"
    # USDJPY ↑ = USD strong
    return "strong" if pair_direction == "bullish" else "weak"


def index_confirms_pair(
    symbol: str,
    pair_alignment: Dict,
    index_alignment: Dict,
) -> Dict:
    """
    Final index override filter.
    """

    if not pair_alignment["aligned"]:
        return {
            "allowed": False,
            "reason": "Pair structure not aligned",
        }

    if not index_alignment["aligned"]:
        return {
            "allowed": False,
            "reason": "Index structure not aligned",
        }

    usd_pos = usd_position(symbol)
    expected_usd_bias = implied_usd_bias(
        pair_alignment["direction"],
        usd_pos,
    )

    index_direction = index_alignment["direction"]

    # Index direction → USD bias
    index_usd_bias = "strong" if index_direction == "bullish" else "weak"

    if index_usd_bias != expected_usd_bias:
        return {
            "allowed": False,
            "reason": (
                f"Index contradicts USD bias "
                f"(expected {expected_usd_bias}, got {index_usd_bias})"
            ),
        }

    return {
        "allowed": True,
        "reason": None,
    }
