import pandas as pd
from typing import Dict, List, Callable
from app.core.forex_provider import get_forex_provider
from app.core.timeframes import TIMEFRAME_MAP
from app.strategy.structure import evaluate_structure, StructureResult


class MarketDataService:
    """
    Responsible ONLY for:
    - Fetching market data (candles)
    - Passing clean data into the strategy engine

    No execution logic.
    No risk logic.
    """

    def __init__(self):
        self.provider = get_forex_provider()

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 300,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data from Forex provider
        and return a clean pandas DataFrame.
        """

        granularity = TIMEFRAME_MAP[timeframe]

        df = self.provider.fetch_ohlcv(
            instrument=symbol,
            granularity=granularity,
            count=limit,
        )

        return df

    def evaluate_structure_multi_tf(
        self,
        symbol: str,
        timeframes: List[str],
        failure_validator: Callable,
    ) -> Dict[str, StructureResult]:
        """
        Evaluate structure independently on EACH timeframe.

        Returns:
        {
            "1h": StructureResult(...),
            "30m": StructureResult(...),
            "15m": StructureResult(...)
        }
        """

        results: Dict[str, StructureResult] = {}

        for tf in timeframes:
            df = self.fetch_ohlcv(symbol=symbol, timeframe=tf)

            result = evaluate_structure(
                df=df,
                timeframe=tf,
                failure_validator=failure_validator,
            )

            results[tf] = result

        return results
