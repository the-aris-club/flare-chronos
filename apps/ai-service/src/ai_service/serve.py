"""Run the analysis API (ADR-0011).

``AI_SERVICE_JWT_KEY`` (plus optional issuer, audience and algorithms) configures
token validation; ``AI_SERVICE_AUTH=disabled`` runs the local demo without it.
A browser ``EventSource`` cannot send an Authorization header, so the real
frontend reads the stream with ``fetch`` and passes the bearer token.
"""

from __future__ import annotations

import argparse

import uvicorn

from ai_service.api import AuthConfig, create_app


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Serve the Flare-Chronos analysis API."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--mode",
        default="deterministic",
        choices=["deterministic", "live"],
        help="the deterministic harness needs no credential; live calls the model",
    )
    args = parser.parse_args()
    auth = AuthConfig.from_env()
    if auth.disabled:
        print("WARNING: AI_SERVICE_AUTH=disabled; every caller is the demo principal.")
    elif not auth.key:
        raise SystemExit(
            "set AI_SERVICE_JWT_KEY, or AI_SERVICE_AUTH=disabled for the demo"
        )
    uvicorn.run(create_app(mode=args.mode, auth=auth), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
