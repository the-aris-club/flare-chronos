"""System 1 can classify through any OpenAI-compatible chat endpoint."""

from __future__ import annotations

import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, ClassVar

REPO_ROOT = Path(__file__).resolve().parents[1]
for pkg_src in (
    REPO_ROOT / "apps" / "ai-service" / "src",
    REPO_ROOT / "packages" / "harmonization-core" / "src",
):
    if str(pkg_src) not in sys.path:
        sys.path.insert(0, str(pkg_src))

from ai_service.models import (
    EndpointProfile,
    OpenAIStructuredChatModel,
    RequestOptions,
    build_chat_model_for_profile,
)
from ai_service.schemas import SpatioTemporalQueryEntity

CLASSIFICATION_ARGS = {
    "region": "mekong",
    "is_deliberative": False,
    "urgency": False,
    "use_case": "UC-S1.3",
    "confidence": 0.9,
}


class StubHandler(BaseHTTPRequestHandler):
    seen: ClassVar[dict[str, Any]] = {}
    reply: ClassVar[dict[str, Any]] = {}

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        StubHandler.seen = {
            "path": self.path,
            "auth": self.headers.get("Authorization"),
            "body": json.loads(self.rfile.read(length)),
        }
        body = json.dumps(StubHandler.reply).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        pass


def openai_reply(arguments: Any) -> dict[str, Any]:
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [
                        {
                            "id": "call_1",
                            "type": "function",
                            "function": {
                                "name": "classify_request",
                                "arguments": arguments,
                            },
                        }
                    ],
                }
            }
        ]
    }


class TestOpenAIStructuredClassifier(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.server = HTTPServer(("127.0.0.1", 0), StubHandler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        os.environ["TEST_STRUCTURED_KEY"] = "k-123"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()

    def model(self) -> OpenAIStructuredChatModel:
        profile = EndpointProfile(
            protocol="openai_structured",
            endpoint=f"http://127.0.0.1:{self.server.server_port}/v1/chat/completions",
            model_id="any-model",
            api_key_env="TEST_STRUCTURED_KEY",
            request=RequestOptions(timeout_ms=5000),
        )
        built = build_chat_model_for_profile(profile)
        assert isinstance(built, OpenAIStructuredChatModel)
        return built

    def entity(self) -> SpatioTemporalQueryEntity:
        return SpatioTemporalQueryEntity(region="mekong")

    def test_the_profile_builds_the_structured_output_client(self) -> None:
        self.assertIsInstance(self.model(), OpenAIStructuredChatModel)

    def test_it_forces_the_classification_tool_and_authenticates(self) -> None:
        StubHandler.reply = openai_reply(json.dumps(CLASSIFICATION_ARGS))
        self.model().classify("lookup 2024 mekong", {}, self.entity())
        seen = StubHandler.seen
        self.assertEqual(seen["auth"], "Bearer k-123")
        self.assertEqual(
            seen["body"]["tool_choice"],
            {"type": "function", "function": {"name": "classify_request"}},
        )
        self.assertEqual(
            seen["body"]["tools"][0]["function"]["name"], "classify_request"
        )
        self.assertEqual(seen["body"]["model"], "any-model")

    def test_arguments_arrive_as_a_json_string_and_are_parsed(self) -> None:
        StubHandler.reply = openai_reply(json.dumps(CLASSIFICATION_ARGS))
        answers = self.model().classify("lookup 2024 mekong", {}, self.entity())
        self.assertEqual(answers["answers"]["use_case"]["choice"], "UC-S1.3")
        self.assertEqual(answers["answers"]["region"]["choice"], "mekong")
        self.assertEqual(answers["confidence_source"], "self_reported")

    def test_an_endpoint_without_an_http_scheme_is_a_fallback_eligible_error(
        self,
    ) -> None:
        from ai_service.models import EndpointCallError, _post_json

        for url in ("file:///etc/passwd", "localhost:11434/v1/chat/completions"):
            with self.subTest(url=url), self.assertRaises(EndpointCallError) as ctx:
                _post_json(url, {}, {}, 1.0)
            self.assertFalse(ctx.exception.retryable)

    def test_a_reply_without_a_classification_call_is_an_error(self) -> None:
        StubHandler.reply = {
            "choices": [{"message": {"role": "assistant", "content": "hi"}}]
        }
        with self.assertRaises(Exception) as ctx:
            self.model().classify("lookup", {}, self.entity())
        self.assertIn("classification", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
