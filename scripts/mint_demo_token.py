"""Mint a short-lived bearer token for ai-service (ADR-0011, ADR-0016).

Tokens are issued out of band: the service only validates them. Run with the same
``AI_SERVICE_JWT_KEY`` the service was started with, then paste the output into the
Workbench. Roles ``approver`` may decide sign-off requests.

    AI_SERVICE_JWT_KEY=... uv run python scripts/mint_demo_token.py --sub nasa-examiner --roles approver
"""

from __future__ import annotations

import argparse
import os
import time

import jwt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sub", required=True)
    parser.add_argument("--name", default="")
    parser.add_argument("--roles", default="")
    parser.add_argument("--hours", type=float, default=8.0)
    args = parser.parse_args()

    key = os.environ.get("AI_SERVICE_JWT_KEY")
    if not key:
        raise SystemExit(
            "set AI_SERVICE_JWT_KEY to the key the service was started with"
        )

    claims: dict[str, object] = {
        "sub": args.sub,
        "roles": [r for r in args.roles.split(",") if r],
        "exp": int(time.time() + args.hours * 3600),
    }
    if args.name:
        claims["name"] = args.name
    print(jwt.encode(claims, key, algorithm="HS256"))


if __name__ == "__main__":
    main()
