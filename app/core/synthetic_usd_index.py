# app/strategy/synthetic_usd_index.py

from typing import Dict, List, Optional

from app.core.market_data import MarketDataService
from app.strategy.structure import StructureResult
from app.strategy.alignment import evaluate_alignment


USD_BASKET = [
    "EUR/USD",
    "GBP/USD",
    "USD/JPY",
]


def invert_direction(direction: str) -> str:
    """
    Invert structure direction for quote-currency pairs.
    EUR/USD bearish → USD bullish
    """
    if direction == "bullish":
        return "bearish"
    if direction == "bearish":
        return "bullish"
    return direction


def evaluate_usd_index(
    market_data: MarketDataService,
    timeframes: List[str],
    failure_validator: callable,
) -> Optional[str]:
    """
    Returns:
    - "bullish"  → USD strength
    - "bearish"  → USD weakness
    - None       → no clear USD bias
    """

    usd_votes: List[str] = []

    for symbol in USD_BASKET:
        structures = market_data.evaluate_structure_multi_tf(
            symbol=symbol,
            timeframes=timeframes,
            failure_validator=failure_validator,
        )

        aligned = evaluate_alignment(structures)

        if not aligned:
            continue

        direction = aligned["direction"]

        # If USD is quote currency, invert
        if symbol.startswith(("EUR/", "GBP/")):
            direction = invert_direction(direction)

        usd_votes.append(direction)

    if not usd_votes:
        return None

    bullish_count = usd_votes.count("bullish")
    bearish_count = usd_votes.count("bearish")

    if bullish_count > bearish_count:
        return "bullish"

    if bearish_count > bullish_count:
        return "bearish"

    return None
