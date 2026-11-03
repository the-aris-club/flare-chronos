"""Write five dev and five examiner bearer tokens to ``.credentials`` (git-ignored).

Tokens look like ``fc-dev-<jwt>`` and ``fc-examiner-<jwt>``. Both roles may decide
sign-off requests (ADR-0016); the prefix only says whose token it is. Run with the key
the service was started with:

    AI_SERVICE_JWT_KEY=... pnpm credentials
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from mint_demo_token import mint

ROLES = {"dev": "Dev", "examiner": "NASA Examiner"}
OUT = Path(__file__).resolve().parent.parent / ".credentials"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--days", type=float, default=30.0)
    args = parser.parse_args()

    key = os.environ.get("AI_SERVICE_JWT_KEY")
    if not key:
        raise SystemExit(
            "set AI_SERVICE_JWT_KEY to the key the service was started with"
        )

    exp = int(time.time() + args.days * 86400)
    lines = [f"# expires in {args.days:g} days; one token per line; do not commit"]
    for role, title in ROLES.items():
        for n in range(1, args.count + 1):
            claims = {
                "sub": f"{role}-{n}",
                "name": f"{title} {n}",
                "roles": ["approver"],
                "exp": exp,
            }
            lines.append(f"{role}-{n}\t{mint(key, claims, f'fc-{role}-')}")

    OUT.write_text("\n".join(lines) + "\n")
    OUT.chmod(0o600)
    print(f"wrote {args.count * len(ROLES)} tokens to {OUT.name}")


if __name__ == "__main__":
    main()
