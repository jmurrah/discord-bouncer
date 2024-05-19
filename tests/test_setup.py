import logging
import os
from unittest.mock import MagicMock, patch

import pytest

from discord_bouncer import setup


@patch("os.getenv")
@patch.dict("os.environ", {})
def test_load_secrets_into_env(mock_getenv, mock_secretmanager_client):
    mock_getenv.return_value = "test_project"
    mock_secret = MagicMock()
    mock_secret.name = "projects/test_project/secrets/test_secret"

    mock_secretmanager_instance = MagicMock()
    mock_secretmanager_instance.list_secrets.return_value = [mock_secret]
    mock_secretmanager_instance.access_secret_version.return_value.payload.data.decode.return_value = (
        "test_secret_value"
    )
    mock_secretmanager_client.return_value = mock_secretmanager_instance

    setup.load_secrets_into_env()

    mock_getenv.assert_called_once_with("GOOGLE_CLOUD_PROJECT")
    mock_secretmanager_client.return_value.list_secrets.assert_called_once_with(
        request={"parent": "projects/test_project"}
    )
    mock_secretmanager_client.return_value.access_secret_version.assert_called_once_with(
        request={"name": "projects/test_project/secrets/test_secret/versions/latest"}
    )
    assert os.environ["test_secret"] == "test_secret_value"


@patch("apscheduler.schedulers.background.BackgroundScheduler.add_job")
@patch("apscheduler.schedulers.background.BackgroundScheduler.start")
def test_initialize_member_expiration_check(mock_add_job, mock_start, caplog):
    caplog.set_level(logging.INFO)

    setup.initialize_member_expiration_check()

    assert "Setting up member expiration check." in caplog.text
    mock_add_job.assert_called_once()
    mock_start.assert_called_once()


def test_setup_environment(
    mock_load_secrets_into_env, mock_initialize_member_expiration_check, caplog
):
    caplog.set_level(logging.INFO)

    setup.setup_environment()

    assert "Setting up environment." in caplog.text
    mock_load_secrets_into_env.assert_called_once()
    mock_initialize_member_expiration_check.assert_called_once()


@pytest.fixture
def mock_secretmanager_client():
    with patch("google.cloud.secretmanager.SecretManagerServiceClient") as mock_client:
        yield mock_client


@pytest.fixture
def mock_load_secrets_into_env():
    with patch("discord_bouncer.setup.load_secrets_into_env") as mock_load:
        yield mock_load


@pytest.fixture
def mock_initialize_member_expiration_check():
    with patch(
        "discord_bouncer.setup.initialize_member_expiration_check"
    ) as mock_initialize:
        yield mock_initialize
