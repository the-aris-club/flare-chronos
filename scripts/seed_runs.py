"""Seed Review with real runs through a running ai-service (ADR-0016).

Each run goes through the live System 1 / System 2 chain and pauses at the sign-off
gate, so the queue holds genuine, undecided runs. Nothing here is a fixture.

    AI_SERVICE_TOKEN=<token> uv run python scripts/seed_runs.py [--url http://127.0.0.1:8765]
"""

from __future__ import annotations

import argparse
import os
import sys
import urllib.parse

import httpx

RUNS = [
    (
        "UC-2.2",
        "UC-2.2 Compute uncertainty-aware tactical dispatch for rangers in mekong in 2024.",
    ),
    ("UC-S1.4", "UC-S1.4 Generate flash NRT tactical ranger alert for amazon in 2026."),
    (
        "UC-2.2",
        "UC-2.2 Compute uncertainty-aware tactical dispatch for rangers in amazon in 2024.",
    ),
    ("UC-S1.4", "UC-S1.4 Generate flash NRT tactical ranger alert for mekong in 2026."),
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    args = parser.parse_args()
    token = os.environ.get("AI_SERVICE_TOKEN")
    if not token:
        print("set AI_SERVICE_TOKEN to a token the service accepts", file=sys.stderr)
        return 2

    failures = 0
    for use_case, query in RUNS:
        params = urllib.parse.urlencode({"use_case_id": use_case, "query": query})
        response = httpx.get(
            f"{args.url}/api/v1/analysis/stream?{params}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=600,
        )
        paused = "event: run_paused" in response.text
        failed = "event: run_failed" in response.text
        print(
            f"{use_case}: HTTP {response.status_code} paused={paused} failed={failed}"
        )
        failures += int(response.status_code != 200 or failed or not paused)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
