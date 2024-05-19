from unittest.mock import patch

import pytest


@pytest.fixture
def mock_firestore_client():
    with patch("google.cloud.firestore.Client") as mock_client:
        yield mock_client
