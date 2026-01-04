import ccxt
import pandas as pd
from typing import Dict, List

from app.strategy.structure import evaluate_structure, StructureResult


class MarketDataService:
    def __init__(self, exchange: ccxt.Exchange):
        self.exchange = exchange

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 300,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV data and return as DataFrame.
        """
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

        df = pd.DataFrame(
            ohlcv,
            columns=["timestamp", "open", "high", "low", "close", "volume"],
        )

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df

    def evaluate_structure_multi_tf(
        self,
        symbol: str,
        timeframes: List[str],
        failure_validator: callable,
    ) -> Dict[str, StructureResult]:
        """
        Evaluate structure for EACH timeframe independently.
        """
        results: Dict[str, StructureResult] = {}

        for tf in timeframes:
            df = self.fetch_ohlcv(symbol, tf)

            result = evaluate_structure(
                df=df,
                timeframe=tf,
                failure_validator=failure_validator,
            )

            results[tf] = result

        return results
