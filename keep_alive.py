"""
keep_alive.py — Pings HF Spaces to prevent sleep after 48h inactivity.

The script:
  1. Hits the Streamlit health endpoint to verify each Space is alive
  2. Hits the main app page to simulate a user visit (counts as activity)

Usage:
    python keep_alive.py

Schedule via GitHub Actions (.github/workflows/keep_alive.yml) — runs every 23 hours.
"""
import urllib.request
import urllib.error
import time
from datetime import datetime, timezone

SPACES = [
    "https://stats-powered-ai-statdetectllm.hf.space",
    "https://anonymouspapersubmission123-statdetectllm.hf.space",
]
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


def run_keep_alive(attempts: int = MAX_ATTEMPTS, retry_delay: int = RETRY_DELAY_SECONDS) -> int:
    """Retry the health/page checks for all spaces to tolerate temporary wake-up outages."""
    exit_code = 0
    for space_url in SPACES:
        health_url = f"{space_url}/_stcore/health"
        label_prefix = space_url.split("//", 1)[-1]
        for attempt in range(1, attempts + 1):
            ok1 = ping(health_url, f"Health check   [{label_prefix}]")
            ok2 = ping(space_url,  f"App page visit [{label_prefix}]")
            if ok1 and ok2:
                break

            if attempt < attempts:
                ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                print(f"[{ts}] WARN Retrying both checks in {retry_delay}s (attempt {attempt + 1}/{attempts})")
                time.sleep(retry_delay)
        else:
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    raise SystemExit(run_keep_alive())
