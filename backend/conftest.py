import pytest
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_visitor_quota(request):
    # Unit tests must not access AWS DynamoDB.
    # Production quota enforcement remains unchanged.
    if request.node.name == "test_ten_questions_allowed_eleventh_rejected":
        yield
        return
    with patch("main.reserve_visitor_question", return_value=True):
        yield
