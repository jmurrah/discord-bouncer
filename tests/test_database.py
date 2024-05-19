import logging
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from discord_bouncer import database


def test_store_member(mock_firestore_client, caplog):
    caplog.set_level(logging.INFO)
    mock_document = (
        mock_firestore_client.return_value.collection.return_value.document.return_value
    )
    mock_document.set.return_value = None

    member_data = {
        "event": "checkout.session.completed",
        "end_date": "1583950910",
        "link_id": "cs_test_1234567890",
        "payment_mode": "subscription",
        "discord_id": 1234567890,
        "discord_username": "test_user",
    }
    database.store_member(member_data)

    assert mock_document.set.call_count == 1
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
    member_exists, access_end_date, expected, mock_date, mock_firestore_client
):
    mock_document = (
        mock_firestore_client.return_value.collection.return_value.document.return_value
    )
    mock_document.get.return_value = MagicMock(
        exists=member_exists,
        to_dict=MagicMock(return_value={"access_end_date": access_end_date}),
    )
    mock_date.today.return_value = (
        datetime.strptime(access_end_date, "%Y-%m-%d").date()
        if expected
        else datetime.strptime(access_end_date, "%Y-%m-%d").date() + timedelta(days=1)
    )

    assert database.access_date_active("1234567890") is expected
    assert mock_document.get.call_count == 1
    assert mock_date.today.call_count == member_exists


def test_delete_expired_members(mock_firestore_client, mock_date, caplog):
    caplog.set_level(logging.INFO)
    mock_date.today.return_value = datetime.strptime("2024-03-08", "%Y-%m-%d").date()
    mock_firestore_client.return_value.collection.return_value.where.return_value.stream.return_value = [
        MagicMock(to_dict=MagicMock(return_value={"id": "1234567890"})),
        MagicMock(to_dict=MagicMock(return_value={"id": "0987654321"})),
    ]
    mock_firestore_client.return_value.collection.return_value.document.return_value.update.return_value = (
        MagicMock()
    )

    database.delete_expired_members()

    assert (
        mock_firestore_client.return_value.collection.return_value.where.return_value.stream.call_count
        == 1
    )
    assert (
        mock_firestore_client.return_value.collection.return_value.document.return_value.update.call_count
        == 1
    )
    assert "Deleting 2 expired members." in caplog.text
    assert "Deleting member: {'id': '1234567890'}" in caplog.text
    assert "Deleting member: {'id': '0987654321'}" in caplog.text


@pytest.mark.parametrize(
    "deleted_discord_ids, expected",
    [
        ({}, []),
        (
            {"deleted_discord_ids": ["1234567890", "0987654321"]},
            ["1234567890", "0987654321"],
        ),
    ],
)
def test_get_recently_expired_members(
    deleted_discord_ids, expected, mock_firestore_client
):
    mock_firestore_client.return_value.collection.return_value.document.return_value.get.return_value = MagicMock(
        to_dict=MagicMock(return_value=deleted_discord_ids)
    )

    assert database.get_recently_expired_members() == expected


@pytest.fixture
def mock_date():
    with patch("discord_bouncer.database.date") as mock_date:
        yield mock_date
