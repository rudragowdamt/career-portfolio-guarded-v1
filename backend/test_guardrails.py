import os
import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import main
from fastapi.testclient import TestClient

client = TestClient(main.app)

def test_bedrock_disabled_by_default():
    with patch.dict(os.environ, {"AI_MODE": "bedrock", "AI_ENABLED": "false"}):
        with patch.object(main, "bedrock_answer", side_effect=AssertionError("Bedrock must not be called")):
            assert os.getenv("AI_ENABLED") == "false"
            assert main.os.getenv("AI_ENABLED") != "true"

def test_quota_rejected_without_database():
    with patch.dict(os.environ, {"QUOTA_TABLE": ""}):
        assert main.reserve_quota("192.0.2.10") is False

def test_cache_requires_database():
    from answer_cache import get_cached_answer
    with patch.dict(os.environ, {"QUOTA_TABLE": ""}):
        assert get_cached_answer("What AWS projects were built?") is None

def test_missing_gateway_identity_is_rejected():
    with patch.object(main, "allowed", return_value=True):
        response = client.post("/chat", json={"question": "What AWS projects were built?"})
        assert response.status_code in (200, 503)


def test_kill_switch_blocks_real_chat_call():
    from unittest.mock import patch
    from fastapi.testclient import TestClient

    with patch.object(main, "MODE", "bedrock"), \
         patch.dict(os.environ, {"AI_ENABLED": "false"}), \
         patch.object(main, "allowed", return_value=True), \
         patch.object(main, "bedrock_answer", side_effect=AssertionError("Bedrock invoked")), \
         patch.object(main, "reserve_quota", side_effect=AssertionError("Quota invoked")):

        response = TestClient(main.app).post(
            "/chat",
            json={"question": "What AWS projects were built?"}
        )

        assert response.status_code == 200
        assert response.json()["mode"] == "fallback"


def test_cache_hit_skips_bedrock_and_quota():
    from unittest.mock import patch
    from fastapi.testclient import TestClient

    with patch.object(main, "MODE", "bedrock"), \
         patch.dict(os.environ, {"AI_ENABLED": "true"}), \
         patch.object(main, "allowed", return_value=True), \
         patch.object(main, "get_cached_answer", return_value="Verified cached career answer"), \
         patch.object(main, "reserve_quota", side_effect=AssertionError("Quota should not be reserved")), \
         patch.object(main, "bedrock_answer", side_effect=AssertionError("Bedrock should not be called")):

        response = TestClient(main.app).post(
            "/chat",
            json={"question": "What AWS projects were built?"}
        )

        assert response.status_code == 200
        assert response.json()["mode"] == "cache"
        assert response.json()["answer"] == "Verified cached career answer"


def test_daily_visitor_limit_blocks_chat():
    from unittest.mock import patch
    from fastapi.testclient import TestClient

    with patch.object(main, "allowed", return_value=True), \
         patch.object(main, "reserve_visitor_question", return_value=False), \
         patch.object(main, "get_cached_answer", side_effect=AssertionError("Cache accessed")), \
         patch.object(main, "bedrock_answer", side_effect=AssertionError("Bedrock invoked")):

        response = TestClient(main.app).post(
            "/chat",
            json={"question": "What AWS projects were built?"}
        )

        assert response.status_code == 429
        assert response.json()["detail"] == "Daily question limit reached"


def test_ten_questions_allowed_eleventh_rejected():
    from unittest.mock import patch
    from botocore.exceptions import ClientError

    class FakeTable:
        def __init__(self):
            self.count = 0

        def update_item(self, **kwargs):
            limit = kwargs["ExpressionAttributeValues"][":limit"]
            if self.count >= limit:
                raise ClientError(
                    {"Error": {"Code": "ConditionalCheckFailedException"}},
                    "UpdateItem"
                )
            self.count += 1

    table = FakeTable()

    class FakeDynamo:
        def Table(self, name):
            return table

    with patch.dict(os.environ, {
        "QUOTA_TABLE": "test-quota-table",
        "VISITOR_HASH_SALT": "test-only-secret",
        "PER_VISITOR_DAILY": "10"
    }), patch("boto3.resource", return_value=FakeDynamo()):
        results = [
            main.reserve_visitor_question("192.0.2.10")
            for _ in range(11)
        ]

    assert results == [True] * 10 + [False]
    assert table.count == 10
