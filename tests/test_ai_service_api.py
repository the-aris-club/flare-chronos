"""The web-facing analysis API: identity-bound sign-off, audit trail, stream."""

from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
import tempfile
import time
import unittest
from pathlib import Path

import jwt
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
for pkg_src in (
    REPO_ROOT / "apps" / "ai-service" / "src",
    REPO_ROOT / "packages" / "harmonization-core" / "src",
):
    if str(pkg_src) not in sys.path:
        sys.path.insert(0, str(pkg_src))

from ai_service.api import AuthConfig, create_app
from ai_service.harness import FlareChronosDualSystemHarness
from ai_service.store import RunStore

SECRET = "test-secret-with-at-least-thirty-two-bytes"
SIGN_OFF_QUERY = "/api/v1/analysis/stream?use_case_id=UC-S1.4&query=UC-S1.4+flash+alert+for+amazon+2026"


def token(sub: str, roles: tuple[str, ...] = ()) -> dict[str, str]:
    claims = {"sub": sub, "roles": list(roles), "exp": int(time.time()) + 3600}
    encoded = jwt.encode(claims, SECRET, algorithm="HS256")
    return {"Authorization": f"Bearer {encoded}"}


class ApiCase(unittest.TestCase):
    run_timeout_s = 60.0

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "service.sqlite"
        self.store = RunStore(self.db)
        self.app = create_app(
            harness=FlareChronosDualSystemHarness(mode="deterministic"),
            store=self.store,
            auth=AuthConfig(key=SECRET, algorithms=("HS256",)),
            run_timeout_s=self.run_timeout_s,
        )
        self.client = TestClient(self.app)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def start_signoff_run(self, who: str, thread_id: str | None = None) -> str:
        url = SIGN_OFF_QUERY + (f"&thread_id={thread_id}" if thread_id else "")
        response = self.client.get(url, headers=token(who))
        self.assertEqual(response.status_code, 200)
        self.assertIn("event: sign_off_required", response.text)
        self.assertIn("event: run_paused", response.text)
        started = next(
            line
            for line in response.text.splitlines()
            if line.startswith("data:") and "run_started" in line
        )
        return json.loads(started[5:])["thread_id"]


class TestAuthentication(ApiCase):
    def test_a_request_without_a_token_is_refused(self) -> None:
        self.assertEqual(self.client.get("/api/v1/analysis/use-cases").status_code, 401)

    def test_a_token_signed_with_the_wrong_key_is_refused(self) -> None:
        bad = jwt.encode(
            {"sub": "x"}, "another-secret-another-secret-123456", algorithm="HS256"
        )
        response = self.client.get(
            "/api/v1/analysis/use-cases", headers={"Authorization": f"Bearer {bad}"}
        )
        self.assertEqual(response.status_code, 401)

    def test_a_token_without_an_expiry_is_refused(self) -> None:
        forever = jwt.encode({"sub": "ana"}, SECRET, algorithm="HS256")
        response = self.client.get(
            "/api/v1/analysis/use-cases", headers={"Authorization": f"Bearer {forever}"}
        )
        self.assertEqual(response.status_code, 401)

    def test_a_token_without_a_subject_is_refused(self) -> None:
        bare = jwt.encode(
            {"roles": [], "exp": int(time.time()) + 3600}, SECRET, algorithm="HS256"
        )
        response = self.client.get(
            "/api/v1/analysis/use-cases", headers={"Authorization": f"Bearer {bare}"}
        )
        self.assertEqual(response.status_code, 401)

    def test_the_use_cases_are_listed_for_a_valid_token(self) -> None:
        response = self.client.get("/api/v1/analysis/use-cases", headers=token("ana"))
        self.assertEqual(response.status_code, 200)
        ids = [item["id"] for item in response.json()["use_cases"]]
        self.assertEqual(len(ids), 20)


class TestStream(ApiCase):
    def test_the_stream_reports_a_run_as_numbered_events(self) -> None:
        response = self.client.get(
            "/api/v1/analysis/stream?use_case_id=UC-S1.3&query=UC-S1.3+fast+lookup+for+2024+mekong",
            headers=token("ana"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("event: run_started", response.text)
        self.assertIn("event: briefing", response.text)
        self.assertIn("event: run_completed", response.text)
        self.assertIn("id: 1\n", response.text)

    def test_a_request_without_a_query_is_refused(self) -> None:
        response = self.client.get("/api/v1/analysis/stream", headers=token("ana"))
        self.assertEqual(response.status_code, 400)

    def test_a_thread_id_cannot_be_taken_from_its_owner(self) -> None:
        self.start_signoff_run("ana", thread_id="shared-thread")
        response = self.client.get(
            SIGN_OFF_QUERY + "&thread_id=shared-thread", headers=token("bo")
        )
        self.assertEqual(response.status_code, 403)

    def test_a_run_that_overruns_its_budget_fails_cleanly(self) -> None:
        async def never(*_a, **_k):
            await asyncio.sleep(5)
            yield  # pragma: no cover

        self.app.state.harness.astream_use_case = never  # type: ignore[method-assign]
        self.app.state.run_timeout_s = 0.05
        response = self.client.get(
            "/api/v1/analysis/stream?query=anything", headers=token("ana")
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("event: run_failed", response.text)
        self.assertIn("time budget", response.text)


class TestSignOff(ApiCase):
    def resume(self, who: str, thread_id: str, **body: object):
        payload = {
            "thread_id": thread_id,
            "approved": True,
            "reason": "checked",
            **body,
        }
        return self.client.post(
            "/api/v1/analysis/resume",
            json=payload,
            headers=token(who, ("approver",) if who == "chief" else ()),
        )

    def test_the_owner_can_release_their_own_run(self) -> None:
        thread = self.start_signoff_run("ana")
        response = self.resume("ana", thread)
        self.assertEqual(response.status_code, 200)
        self.assertIn("event: run_completed", response.text)

    def test_someone_who_is_not_the_owner_cannot_approve(self) -> None:
        thread = self.start_signoff_run("ana")
        self.assertEqual(self.resume("bo", thread).status_code, 403)

    def test_an_assigned_approver_can_release_someone_elses_run(self) -> None:
        thread = self.start_signoff_run("ana")
        self.assertEqual(self.resume("chief", thread).status_code, 200)

    def test_decided_by_in_the_body_is_ignored(self) -> None:
        thread = self.start_signoff_run("ana")
        self.resume("ana", thread, decided_by="the-minister")
        row = self.store.decisions(thread)[0]
        self.assertEqual(row["principal"], "ana")

    def test_every_decision_is_written_to_the_audit_record(self) -> None:
        thread = self.start_signoff_run("ana")
        self.resume("ana", thread, approved=False, reason="not verified")
        rows = self.store.decisions(thread)
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["approved"], rows[0]["reason"]), (0, "not verified"))

    def test_the_audit_record_cannot_be_rewritten(self) -> None:
        thread = self.start_signoff_run("ana")
        self.resume("ana", thread)
        with sqlite3.connect(self.db) as raw:
            with self.assertRaises(sqlite3.DatabaseError):
                raw.execute("UPDATE audit SET approved = 0")
            with self.assertRaises(sqlite3.DatabaseError):
                raw.execute("DELETE FROM audit")

    def test_a_run_that_asked_for_no_sign_off_cannot_be_decided(self) -> None:
        done = self.client.get(
            "/api/v1/analysis/stream?use_case_id=UC-S1.3&query=UC-S1.3+lookup+2024+mekong&thread_id=plain",
            headers=token("ana"),
        )
        self.assertIn("event: run_completed", done.text)
        self.assertEqual(self.resume("ana", "plain").status_code, 409)
        self.assertEqual(self.store.decisions("plain"), [])

    def test_a_sign_off_request_can_be_decided_only_once(self) -> None:
        thread = self.start_signoff_run("ana")
        self.assertEqual(self.resume("ana", thread).status_code, 200)
        self.assertEqual(self.resume("ana", thread, approved=False).status_code, 409)
        self.assertEqual(len(self.store.decisions(thread)), 1)

    def test_an_unknown_thread_is_not_found(self) -> None:
        self.assertEqual(self.resume("ana", "no-such-thread").status_code, 404)

    def test_a_resume_without_a_thread_is_refused(self) -> None:
        response = self.client.post(
            "/api/v1/analysis/resume", json={"approved": True}, headers=token("ana")
        )
        self.assertEqual(response.status_code, 422)


class TestProductionLifespan(unittest.TestCase):
    """The deployed app builds its own harness on a durable async checkpointer."""

    def test_a_paused_run_streams_fully_and_resumes_on_the_async_saver(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            app = create_app(
                store=RunStore(Path(tmp) / "service.sqlite"),
                auth=AuthConfig(key=SECRET, algorithms=("HS256",)),
                checkpoint_path=Path(tmp) / "checkpoints.sqlite",
            )
            with TestClient(app) as client:
                paused = client.get(
                    SIGN_OFF_QUERY + "&thread_id=prod", headers=token("ana")
                )
                self.assertIn("event: run_paused", paused.text)
                self.assertNotIn("run_failed", paused.text)
                done = client.post(
                    "/api/v1/analysis/resume",
                    json={"thread_id": "prod", "approved": True},
                    headers=token("ana"),
                )
                self.assertIn("event: run_completed", done.text)


class TestDemoBinding(unittest.TestCase):
    def test_the_unauthenticated_demo_refuses_a_public_address(self) -> None:
        from ai_service.serve import check_bind

        with self.assertRaises(SystemExit):
            check_bind("0.0.0.0", AuthConfig(disabled=True))  # noqa: S104
        check_bind("127.0.0.1", AuthConfig(disabled=True))
        check_bind("0.0.0.0", AuthConfig(key=SECRET))  # noqa: S104


class TestRestartSafety(unittest.TestCase):
    def test_ownership_and_audit_survive_a_restart(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "service.sqlite"
            first = RunStore(db)
            first.claim("t1", "ana")
            first.record_decision("t1", "ana", True, "ok")
            second = RunStore(db)
            self.assertEqual(second.owner_of("t1"), "ana")
            self.assertEqual(len(second.decisions("t1")), 1)


class TestOpenApiContract(ApiCase):
    def test_the_contract_declares_bearer_auth_and_the_event_stream(self) -> None:
        schema = self.app.openapi()
        self.assertIn("HTTPBearer", schema["components"]["securitySchemes"])
        stream = schema["paths"]["/api/v1/analysis/stream"]["get"]
        self.assertIn("text/event-stream", stream["responses"]["200"]["content"])
        self.assertTrue(stream.get("security"))
        for status in ("400", "401", "403"):
            self.assertIn(status, stream["responses"])
        resume = schema["paths"]["/api/v1/analysis/resume"]["post"]
        for status in ("401", "403", "404", "409"):
            self.assertIn(status, resume["responses"])

    def test_the_published_schema_matches_the_app(self) -> None:
        snapshot = REPO_ROOT / "docs" / "openapi" / "ai-service.json"
        self.assertEqual(json.loads(snapshot.read_text()), self.app.openapi())


if __name__ == "__main__":
    unittest.main()
