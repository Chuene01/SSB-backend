from fastapi import APIRouter
from typing import Dict

from app.core.exchange import get_exchange
from app.core.market_data import MarketDataService
from app.strategy.alignment import evaluate_alignment
from app.strategy.index_filter import index_confirms_pair
from app.strategy.candles import validate_entry_candle

router = APIRouter()


@router.get("/")
def get_signal() -> Dict:
    # =========================
    # Configuration (temporary)
    # =========================
    symbol = "EUR/USD"
    index_symbol = "DXY"   # handled by exchange adapter
    timeframes = ["1h", "30m", "15m"]

    market_data = MarketDataService()

    # =========================
    # 1️⃣ Pair structure
    # =========================
    pair_structures = market_data.evaluate_structure_multi_tf(
        symbol=symbol,
        timeframes=timeframes,
        failure_validator=lambda idx: True,  # already validated in Phase 2A
    )

    pair_alignment = evaluate_alignment(pair_structures)

    if not pair_alignment["aligned"]:
        return {
            "trade_allowed": False,
            "reason": "Pair structure not aligned",
            "details": pair_alignment,
        }

    # =========================
    # 2️⃣ Index structure
    # =========================
    index_structures = market_data.evaluate_structure_multi_tf(
        symbol=index_symbol,
        timeframes=timeframes,
        failure_validator=lambda idx: True,
    )

    index_alignment = evaluate_alignment(index_structures)

    index_check = index_confirms_pair(
        symbol=symbol,
        pair_alignment=pair_alignment,
        index_alignment=index_alignment,
    )

    if not index_check["allowed"]:
        return {
            "trade_allowed": False,
            "reason": index_check["reason"],
        }

    # =========================
    # 3️⃣ Select dominant zone
    # =========================
    # Take the first valid zone from aligned TFs
    direction = pair_alignment["direction"]
    aligned_tfs = pair_alignment["valid_timeframes"]

    zone = None
    zone_tf = None

    for tf in aligned_tfs:
        result = pair_structures[tf]
        if result.zone:
            zone = result.zone
            zone_tf = tf
            break

    if not zone:
        return {
            "trade_allowed": False,
            "reason": "No valid structure zone",
        }

    # =========================
    # 4️⃣ Fetch candles for entry check
    # =========================
    df = market_data.fetch_ohlcv(symbol, zone_tf)
    current_idx = len(df) - 1

    entry_ok = validate_entry_candle(
        df=df,
        idx=current_idx,
        direction=direction,
        zone=(zone.lower, zone.upper),
    )

    if not entry_ok:
        return {
            "trade_allowed": False,
            "reason": "No valid entry candle",
        }

    # =========================
    # ✅ FINAL DECISION
    # =========================
    return {
        "trade_allowed": True,
        "direction": direction,
        "zone": {
            "lower": zone.lower,
            "upper": zone.upper,
            "timeframe": zone_tf,
        },
        "entry_index": current_idx,
        "note": "Phase 2C decision only — no execution",
    }

