"""Tests for the analysis stream server (`ai_service.serve`).

The server is the only place where the harness meets a browser, so these
tests drive it over real HTTP: a page, the event stream, and the resume call
that answers a run waiting for a human.
"""

from __future__ import annotations

import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
for pkg_src in (
    REPO_ROOT / "apps" / "ai-service" / "src",
    REPO_ROOT / "packages" / "harmonization-core" / "src",
):
    if str(pkg_src) not in sys.path:
        sys.path.insert(0, str(pkg_src))

from ai_service.serve import AnalysisRequestHandler, AnalysisServer, ServerState


class TestAnalysisStreamServer(unittest.TestCase):
    """The documented endpoints answer what the architecture document says."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = AnalysisServer(("127.0.0.1", 0), AnalysisRequestHandler)
        cls.server.state = ServerState(mode="deterministic")
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()

    def _get(self, path: str) -> tuple[int, str]:
        with urllib.request.urlopen(f"{self.base}{path}", timeout=30) as response:
            return response.status, response.read().decode("utf-8")

    def _post_json(self, path: str, payload: dict[str, Any]) -> tuple[int, str]:
        request = urllib.request.Request(
            f"{self.base}{path}",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read().decode("utf-8")

    def test_01_the_demo_page_is_served(self) -> None:
        """The page that shows a run exists and names the project."""
        status, body = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn("Flare-Chronos", body)
        self.assertIn("analysis/stream", body)

    def test_02_the_use_cases_are_listed(self) -> None:
        """The page asks the server which analyses exist, so the list cannot drift."""
        status, body = self._get("/api/v1/analysis/use-cases")
        self.assertEqual(status, 200)
        payload = json.loads(body)
        ids = [item["id"] for item in payload["use_cases"]]
        self.assertIn("UC-1.1", ids)
        self.assertEqual(len(ids), 20)

    def test_03_the_stream_reports_the_run_as_events(self) -> None:
        """One run streams typed events and ends with the briefing."""
        status, body = self._get(
            "/api/v1/analysis/stream?use_case_id=UC-S1.3&query=UC-S1.3+fast+lookup+for+2024+mekong"
        )
        self.assertEqual(status, 200)
        self.assertIn("event: run_started", body)
        self.assertIn("event: node_completed", body)
        self.assertIn("event: verification", body)
        self.assertIn("event: briefing", body)
        self.assertIn("event: run_completed", body)

    def test_04_a_free_form_request_needs_a_query(self) -> None:
        """A request without a query is refused rather than run empty."""
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._get("/api/v1/analysis/stream")
        self.assertEqual(ctx.exception.code, 400)

    def test_05_a_run_that_needs_a_person_can_be_answered(self) -> None:
        """A run that authorizes a field action waits, and the answer releases it."""
        status, body = self._get(
            "/api/v1/analysis/stream?use_case_id=UC-S1.4&query=UC-S1.4+flash+alert+for+amazon+2026&thread_id=demo-signoff"
        )
        self.assertEqual(status, 200)
        self.assertIn("event: sign_off_required", body)
        self.assertIn("event: run_paused", body)

        status, body = self._post_json(
            "/api/v1/analysis/resume",
            {
                "thread_id": "demo-signoff",
                "approved": True,
                "reason": "verified on the ground",
                "decided_by": "test-operator",
            },
        )
        self.assertEqual(status, 200)
        self.assertIn("event: run_completed", body)
        self.assertIn("TIER_1_ACTIVE_MONITORING", body)

    def test_06_a_resume_without_a_thread_is_refused(self) -> None:
        """The resume call needs to know which run to continue."""
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._post_json("/api/v1/analysis/resume", {"approved": True})
        self.assertEqual(ctx.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
