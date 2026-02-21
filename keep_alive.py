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
from datetime import datetime, timezone

SPACE_APP_URL = "https://stats-powered-ai-statdetectllm.hf.space"
HEALTH_URL    = f"{SPACE_APP_URL}/_stcore/health"


def ping(url: str, label: str) -> bool:
    """Send a GET request to url and print the result. Returns True on HTTP 2xx."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "keep-alive-bot/1.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            if 200 <= resp.status < 300:
                print(f"[{ts}] OK  {label}: HTTP {resp.status}")
                return True
            else:
                print(f"[{ts}] WARN {label}: unexpected HTTP {resp.status}")
                return False
    except urllib.error.URLError as e:
        print(f"[{ts}] FAIL {label}: {e}")
        return False
    except Exception as e:
        print(f"[{ts}] FAIL {label}: unexpected error: {e}")
        return False


if __name__ == "__main__":
    ok1 = ping(HEALTH_URL,    "Health check  ")
    ok2 = ping(SPACE_APP_URL, "App page visit")
    raise SystemExit(0 if (ok1 and ok2) else 1)
