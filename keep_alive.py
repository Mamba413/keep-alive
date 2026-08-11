"""
keep_alive.py — Pings the HF Space to prevent sleep after 48h inactivity.

The script:
  1. Hits the Streamlit health endpoint to verify the Space is alive
  2. Hits the main app page to simulate a user visit (counts as activity)

Usage:
    python keep_alive.py

Schedule via GitHub Actions (.github/workflows/keep_alive.yml) — runs every 23 hours.
"""
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone

SPACE_APP_URL = "https://stats-powered-ai-statdetectllm.hf.space"
HEALTH_URL    = f"{SPACE_APP_URL}/_stcore/health"
MAX_ATTEMPTS = 4
RETRY_DELAY_SECONDS = 15
RETRYABLE_HTTP_STATUS_CODES = {408, 429}


def ping(url: str, label: str) -> bool:
    """Send a GET request to url and print the result. Returns True on HTTP 2xx."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "keep-alive-bot/1.0"},
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                if 200 <= resp.status < 300:
                    print(f"[{ts}] OK  {label}: HTTP {resp.status} (attempt {attempt}/{MAX_ATTEMPTS})")
                    return True
                print(f"[{ts}] WARN {label}: unexpected HTTP {resp.status} (attempt {attempt}/{MAX_ATTEMPTS})")
                if resp.status < 500 and resp.status not in RETRYABLE_HTTP_STATUS_CODES:
                    return False
        except urllib.error.HTTPError as e:
            print(f"[{ts}] WARN {label}: HTTP {e.code} (attempt {attempt}/{MAX_ATTEMPTS})")
            if e.code < 500 and e.code not in RETRYABLE_HTTP_STATUS_CODES:
                return False
        except urllib.error.URLError as e:
            print(f"[{ts}] WARN {label}: {e} (attempt {attempt}/{MAX_ATTEMPTS})")
        except Exception as e:
            print(f"[{ts}] WARN {label}: unexpected error: {e} (attempt {attempt}/{MAX_ATTEMPTS})")

        if attempt < MAX_ATTEMPTS:
            time.sleep(RETRY_DELAY_SECONDS)

    return False


if __name__ == "__main__":
    ok1 = ping(HEALTH_URL,    "Health check  ")
    ok2 = ping(SPACE_APP_URL, "App page visit")
    raise SystemExit(0 if (ok1 and ok2) else 1)
