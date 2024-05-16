import logging
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from discord_bouncer import discord_actions


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "emoji, access_date_active",
    [("🪃", True), ("💸", True), ("🪃", False), ("💸", False)],
)
async def test_on_raw_reaction_add(
    emoji,
    access_date_active,
    mock_bot,
    mock_access_date_active,
    mock_get_payment_link,
    caplog,
):
    caplog.set_level(logging.INFO)

    mock_channel = MagicMock(spec=discord.TextChannel)
    mock_message = AsyncMock(spec=discord.Message)
    mock_user = MagicMock()

    payload = MagicMock()
    payload.emoji.name = emoji

    mock_channel.fetch_message.return_value = mock_message
    mock_channel.name = discord_actions.REACTION_CHANNEL
    mock_channel.send = AsyncMock()

    mock_user.name = "TestUser"
    mock_user.id = 1234
    mock_user.remove_reaction = AsyncMock()
    mock_user.send = AsyncMock()

    mock_bot.get_channel.return_value = mock_channel
    mock_bot.get_user.return_value = mock_user
    mock_access_date_active.return_value = access_date_active
    mock_get_payment_link.return_value = "https://example.com"

    await discord_actions.on_raw_reaction_add(payload)

    assert "We have logged in as TestBot" in caplog.text


@pytest.mark.asyncio
async def test_on_ready(mock_bot, mock_listen_to_database, caplog):
    caplog.set_level(logging.INFO)
    mock_bot.user = "TestBot"

    await discord_actions.on_ready()

    assert "We have logged in as TestBot" in caplog.text
    mock_listen_to_database.assert_called_once()


@pytest.fixture
def mock_bot():
    with patch("discord_bouncer.discord_actions.BOT") as mock_bot:
        yield mock_bot


@pytest.fixture
def mock_access_date_active():
    with patch(
        "discord_bouncer.discord_actions.access_date_active"
    ) as mock_access_date_active:
        yield mock_access_date_active


@pytest.fixture
def mock_get_payment_link():
    with patch(
        "discord_bouncer.discord_actions.get_payment_link"
    ) as mock_get_payment_link:
        yield mock_get_payment_link


@pytest.fixture
def mock_listen_to_database():
    with patch(
        "discord_bouncer.discord_actions.listen_to_database"
    ) as mock_listen_to_database:
        yield mock_listen_to_database
