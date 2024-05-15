import logging
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from discord_bouncer import database


def test_convert_time_to_date():
    with patch.dict("os.environ", {"TZ": "America/Chicago"}):
        assert database.convert_time_to_date("2024-03-09T02:41:10.000Z") == "2024-03-08"


def test_store_member(mock_convert_time_to_date, mock_firestore_document, caplog):
    caplog.set_level(logging.INFO)
    mock_convert_time_to_date.return_value = "2024-03-08"
    mock_firestore_document.set.return_value = None

    member_data = {
        "event": "checkout.session.completed",
        "time": "2024-03-09T02:41:10.000Z",
        "link_id": "cs_test_1234567890",
        "payment_mode": "subscription",
        "discord_id": 1234567890,
        "discord_username": "test_user",
    }
    database.store_member(member_data)

    assert mock_convert_time_to_date.call_count == 1
    assert mock_firestore_document.set.call_count == 1
    assert f"Stored member: {member_data}" in caplog.text


@pytest.mark.parametrize(
    "member_exists, access_end_date, expected",
    [
        (True, "2024-03-08", True),
        (True, "2024-03-08", False),
        (False, "2024-03-08", False),
    ],
)
def test_access_date_active(
    member_exists, access_end_date, expected, mock_date, mock_firestore_document
):
    mock_firestore_document.get.return_value = MagicMock(
        exists=member_exists,
        to_dict=MagicMock(return_value={"access_end_date": access_end_date}),
    )
    mock_date.today.return_value = (
        datetime.strptime(access_end_date, "%Y-%m-%d").date()
        if expected
        else datetime.strptime(access_end_date, "%Y-%m-%d").date() + timedelta(days=1)
    )

    assert database.access_date_active("1234567890") is expected


@pytest.fixture
def mock_convert_time_to_date():
    with patch("discord_bouncer.database.convert_time_to_date") as mock_convert:
        yield mock_convert


@pytest.fixture
def mock_firestore_document():
    with patch("google.cloud.firestore.Client") as mock_client:
        mock_document = MagicMock()
        mock_client.return_value.collection.return_value.document.return_value = (
            mock_document
        )
        yield mock_document


@pytest.fixture
def mock_date():
    with patch("discord_bouncer.database.date") as mock_date:
        yield mock_date
