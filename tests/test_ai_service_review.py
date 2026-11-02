"""Review Runs are projected from the Run Event Log the service stores (ADR-0016)."""

from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path

from ai_service.store import RunStore
from test_ai_service_api import ApiCase, token

APPROVER = ("approver",)


class TestReviewQueue(ApiCase):
    def test_a_paused_sign_off_run_is_listed_as_needing_a_decision(self) -> None:
        thread = self.start_signoff_run("ana")

        response = self.client.get("/api/v1/review/runs", headers=token("ana"))

        self.assertEqual(response.status_code, 200)
        runs = response.json()["runs"]
        self.assertEqual([r["id"] for r in runs], [thread])
        self.assertEqual(runs[0]["status"], "needs")
        self.assertEqual(runs[0]["use_case_id"], "UC-S1.4")
        self.assertEqual(runs[0]["owner"], "ana")

    def test_another_principal_does_not_see_the_run_but_an_approver_does(self) -> None:
        thread = self.start_signoff_run("ana")

        other = self.client.get("/api/v1/review/runs", headers=token("bob"))
        approver = self.client.get(
            "/api/v1/review/runs", headers=token("carol", APPROVER)
        )

        self.assertEqual(other.json()["runs"], [])
        self.assertEqual([r["id"] for r in approver.json()["runs"]], [thread])

    def test_a_run_that_never_asked_for_sign_off_is_not_a_review_run(self) -> None:
        response = self.client.get(
            "/api/v1/analysis/stream?use_case_id=UC-S1.3&query=UC-S1.3+lookup+mekong+2024",
            headers=token("ana"),
        )
        self.assertEqual(response.status_code, 200)

        runs = self.client.get("/api/v1/review/runs", headers=token("ana"))

        self.assertEqual(runs.json()["runs"], [])


class TestReviewDecision(ApiCase):
    def decide(self, thread: str, who: str, approved: bool, code: str) -> None:
        response = self.client.post(
            "/api/v1/analysis/resume",
            json={
                "thread_id": thread,
                "approved": approved,
                "reason": "checked against the evidence",
                "reason_code": code,
            },
            headers=token(who, APPROVER),
        )
        self.assertEqual(response.status_code, 200)

    def test_an_approval_publishes_the_run_and_is_audited_with_its_reason_code(
        self,
    ) -> None:
        thread = self.start_signoff_run("ana")

        self.decide(thread, "carol", True, "evidence")

        runs = self.client.get("/api/v1/review/runs", headers=token("ana")).json()
        self.assertEqual(runs["runs"][0]["status"], "published")
        audit = self.client.get(
            f"/api/v1/review/runs/{thread}/audit", headers=token("ana")
        ).json()["audit"]
        self.assertEqual(len(audit), 1)
        self.assertEqual(audit[0]["id"], "A-0001")
        self.assertEqual(audit[0]["principal"], "carol")
        self.assertTrue(audit[0]["approved"])
        self.assertEqual(audit[0]["reason_code"], "evidence")

    def test_an_unknown_reason_code_is_refused_before_anything_is_recorded(
        self,
    ) -> None:
        thread = self.start_signoff_run("ana")

        response = self.client.post(
            "/api/v1/analysis/resume",
            json={"thread_id": thread, "approved": True, "reason_code": "because"},
            headers=token("carol", APPROVER),
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(self.store.decisions(thread), [])

    def test_a_rejection_withholds_the_run(self) -> None:
        thread = self.start_signoff_run("ana")

        self.decide(thread, "carol", False, "duplicate")

        runs = self.client.get("/api/v1/review/runs", headers=token("ana")).json()
        self.assertEqual(runs["runs"][0]["status"], "withheld")


class TestReviewRunDetail(ApiCase):
    def test_the_detail_carries_the_evidence_the_reviewer_signs_off_on(self) -> None:
        thread = self.start_signoff_run("ana")

        response = self.client.get(
            f"/api/v1/review/runs/{thread}", headers=token("ana")
        )

        self.assertEqual(response.status_code, 200)
        run = response.json()
        self.assertEqual(run["status"], "needs")
        self.assertTrue(run["briefing"].strip())
        self.assertTrue(run["verification"]["passed"])
        self.assertEqual(run["entity"]["region"], "amazon")
        self.assertGreater(len(run["facts"]), 0)
        fact = run["facts"][0]
        self.assertEqual(
            set(fact), {"fact_key", "value", "unit", "source_tool", "provenance"}
        )
        self.assertTrue(fact["source_tool"].startswith("tool_"))
        self.assertIn("tool_emit_flash_nrt_alert", run["tools"])

    def test_a_stranger_cannot_read_the_detail_or_audit_and_an_unknown_run_is_404(
        self,
    ) -> None:
        thread = self.start_signoff_run("ana")

        for path in (
            f"/api/v1/review/runs/{thread}",
            f"/api/v1/review/runs/{thread}/audit",
        ):
            self.assertEqual(
                self.client.get(path, headers=token("bob")).status_code, 403
            )
        self.assertEqual(
            self.client.get(
                "/api/v1/review/runs/nope", headers=token("ana")
            ).status_code,
            404,
        )


class TestReviewSurvivesRestart(ApiCase):
    def test_the_queue_and_the_audit_outlive_the_service(self) -> None:
        thread = self.start_signoff_run("ana")
        self.client.post(
            "/api/v1/analysis/resume",
            json={"thread_id": thread, "approved": True, "reason_code": "evidence"},
            headers=token("carol", APPROVER),
        )

        reopened = RunStore(self.db)

        self.assertEqual(reopened.runs()[0]["thread_id"], thread)
        self.assertEqual(reopened.decisions(thread)[0]["reason_code"], "evidence")
        self.assertIn("sign_off_required", [e["type"] for e in reopened.events(thread)])

    def test_the_event_log_refuses_updates_and_deletes(self) -> None:
        self.start_signoff_run("ana")

        with sqlite3.connect(self.db) as raw:
            with self.assertRaises(sqlite3.DatabaseError):
                raw.execute("UPDATE events SET type = 'x'")
            with self.assertRaises(sqlite3.DatabaseError):
                raw.execute("DELETE FROM events")

    def test_an_audit_table_from_before_reason_codes_is_migrated_in_place(self) -> None:
        old = Path(self.tmp.name) / "old.sqlite"
        with sqlite3.connect(old) as raw:
            raw.executescript(
                """
                CREATE TABLE runs (thread_id TEXT PRIMARY KEY, owner TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT 'then');
                CREATE TABLE audit (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT NOT NULL, principal TEXT NOT NULL,
                    approved INTEGER NOT NULL, reason TEXT NOT NULL,
                    decided_at TEXT NOT NULL DEFAULT 'then');
                INSERT INTO audit (thread_id, principal, approved, reason)
                    VALUES ('t', 'carol', 1, 'ok');
                """
            )

        store = RunStore(old)
        store.record_decision("t", "dave", False, "no", "stale")

        rows = store.decisions("t")
        self.assertEqual([r["reason_code"] for r in rows], ["", "stale"])
        with sqlite3.connect(old) as raw, self.assertRaises(sqlite3.DatabaseError):
            raw.execute("DELETE FROM audit")


if __name__ == "__main__":
    unittest.main()
