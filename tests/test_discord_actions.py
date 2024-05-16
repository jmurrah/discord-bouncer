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
):
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
@pytest.mark.parametrize(
    "message_content, value_error, should_add_role",
    [
        ("event: checkout.session.completed\ndiscord_id: 1234567890", False, True),
        ("random: text", False, False),
        ("wrong_channel_name", True, False),
        ("should have value error", True, False),
    ],
)
async def test_on_message(
    message_content,
    value_error,
    should_add_role,
    mock_discord_utils,
    mock_store_member,
    mock_add_role,
    caplog,
):
    caplog.set_level(logging.ERROR)

    mock_channel = MagicMock(spec=discord.TextChannel)
    mock_channel.name = (
        discord_actions.PAYMENT_LOGS_CHANNEL
        if "wrong_channel_name" not in message_content
        else "hello_world"
    )

    mock_discord_utils.get.return_value = MagicMock()

    mock_message = MagicMock(spec=discord.Message)
    mock_message.author = "TestUser"
    mock_message.channel = mock_channel
    mock_message.content = message_content
    mock_message.guild.get_member.return_value = MagicMock()
    mock_message.guild.get_role.return_value = MagicMock()

    await discord_actions.on_message(mock_message)

    if "wrong_channel_name" in message_content:
        assert "" == caplog.text
        mock_store_member.assert_not_called()
        mock_add_role.assert_not_called()
        return

    assert (
        "Error parsing message content." in caplog.text
        if value_error
        else "Error parsing message content." not in caplog.text
    )
    (
        mock_store_member.assert_called_once()
        if should_add_role
        else mock_store_member.assert_not_called()
    )
    (
        mock_add_role.assert_called_once()
        if should_add_role
        else mock_add_role.assert_not_called()
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
    with patch("discord_bouncer.discord_actions.access_date_active") as mock_active:
        yield mock_active


@pytest.fixture
def mock_get_payment_link():
    with patch("discord_bouncer.discord_actions.get_payment_link") as mock_get_link:
        yield mock_get_link


@pytest.fixture
def mock_discord_utils():
    with patch("discord_bouncer.discord_actions.discord.utils") as mock_discord_utils:
        yield mock_discord_utils


@pytest.fixture
def mock_store_member():
    with patch("discord_bouncer.discord_actions.store_member") as mock_store_member:
        yield mock_store_member


@pytest.fixture
def mock_add_role():
    with patch("discord_bouncer.discord_actions.add_role") as mock_add_role:
        yield mock_add_role


@pytest.fixture
def mock_listen_to_database():
    with patch("discord_bouncer.discord_actions.listen_to_database") as mock_listen:
        yield mock_listen
