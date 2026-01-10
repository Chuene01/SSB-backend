import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TWELVE_DATA_API_KEY")
BASE_URL = "https://api.twelvedata.com/time_series"


class ForexDataProvider:
    """
    Data-only Forex & Index provider using Twelve Data.
    No execution. No trading logic.
    """

    def fetch_ohlcv(
        self,
        instrument: str,
        granularity: str,
        count: int = 300,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV candles from Twelve Data and return DataFrame.
        """

        params = {
            "symbol": instrument,
            "interval": granularity,
            "outputsize": count,
            "apikey": API_KEY,
            "format": "JSON",
        }

        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()

        payload = response.json()

        if "values" not in payload:
            raise ValueError(f"No data returned for {instrument}: {payload}")

        rows = []
        for c in payload["values"]:
            rows.append({
                "timestamp": pd.to_datetime(c["datetime"]),
                "open": float(c["open"]),
                "high": float(c["high"]),
                "low": float(c["low"]),
                "close": float(c["close"]),
                "volume": float(c.get("volume", 0)),
            })

        df = pd.DataFrame(rows)
        df.sort_values("timestamp", inplace=True)
        df.set_index("timestamp", inplace=True)

        return df


def get_forex_provider() -> ForexDataProvider:
    return ForexDataProvider()
