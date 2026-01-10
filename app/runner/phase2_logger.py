import json
import time
import requests
from datetime import datetime
from pathlib import Path

# =========================
# CONFIGURATION
# =========================

SIGNAL_URL = "http://127.0.0.1:8000/signal"
LOG_INTERVAL_SECONDS = 15 * 60  # 15 minutes

SYMBOL = "EUR/USD"
TIMEFRAMES = ["1h", "30m", "15m"]

LOG_DIR = Path("app/logs/phase2")
LOG_DIR.mkdir(parents=True, exist_ok=True)


# =========================
# HELPERS
# =========================

def get_log_file_path() -> Path:
    """
    One log file per day.
    """
    today = datetime.utcnow().strftime("%Y-%m-%d")
    return LOG_DIR / f"phase2_{today}.jsonl"


def log_entry(entry: dict):
    """
    Append a single JSON entry to the log file.
    """
    log_file = get_log_file_path()
    with log_file.open("a") as f:
        f.write(json.dumps(entry) + "\n")


# =========================
# MAIN LOOP
# =========================

def run_logger():
    print("🟢 Phase 2 logger started")
    print(f"⏱ Interval: {LOG_INTERVAL_SECONDS // 60} minutes")
    print(f"📊 Symbol: {SYMBOL} | TFs: {TIMEFRAMES}")
    print("Press Ctrl+C to stop\n")

    while True:
        timestamp = datetime.utcnow().isoformat()

        try:
            response = requests.get(
                SIGNAL_URL,
                timeout=20,
            )

            response.raise_for_status()
            decision = response.json()

            log_entry({
                "timestamp": timestamp,
                "symbol": SYMBOL,
                "timeframes": TIMEFRAMES,
                **decision,
            })

            print(f"[{timestamp}] Logged decision")

        except Exception as e:
            # Log the error instead of crashing
            log_entry({
                "timestamp": timestamp,
                "error": str(e),
            })

            print(f"[{timestamp}] ❌ Error logged: {e}")

        time.sleep(LOG_INTERVAL_SECONDS)


# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    run_logger()
