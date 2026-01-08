import ccxt


def get_exchange():
    """
    Factory for CCXT exchange.
    Phase 2: data access only (paper / observation).
    """
    exchange = ccxt.binance({
        "enableRateLimit": True,
    })

    return exchange
