import logging
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from discord_bouncer import discord_actions


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "emoji, access_date_active",
    [("🪃", True), ("💸", True), ("🪃", False), ("💸", False), ("🧪", True)],
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

    if emoji in ["🪃", "💸"]:
        mock_message.remove_reaction.assert_called_once_with(emoji, mock_user)
    else:
        mock_message.remove_reaction.assert_not_called()
        return

    if access_date_active:
        mock_channel.send.assert_called_once_with(
            f"{mock_user.name} ({mock_user.id}) already has access to the {discord_actions.PAID_ROLE} Discord Role!"
        )
        mock_user.send.assert_not_called()
    else:
        mock_channel.send.assert_not_called()
        mock_user.send.assert_called_once_with(
            f"Click the link below to {'subscribe' if emoji == '🪃' else 'pay'} for access to the {discord_actions.PAID_ROLE} Discord Role:\nhttps://example.com"
        )


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
