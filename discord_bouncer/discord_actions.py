import asyncio
import logging
import os

import discord
from google.cloud import firestore

from .checkout_session import PAID_ROLE, get_payment_link
from .database import access_date_active, get_recently_expired_members, store_member
from .setup import setup_environment

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

BOT = discord.Bot(command_prefix="!", intents=intents)

REACTION_CHANNEL = "get-trusted-role"
PAYMENT_LOGS_CHANNEL = "payment-logs"
ROLE_LOGS_CHANNEL = "role-logs"
FIRST_CALL = True


@BOT.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    channel = BOT.get_channel(payload.channel_id)
    message = await channel.fetch_message(payload.message_id)
    member = BOT.get_user(payload.user_id)
    emoji = payload.emoji.name

    if (
        not isinstance(channel, discord.TextChannel)
        or channel.name != REACTION_CHANNEL
        or emoji != "💸"
    ):
        return

    logging.info(f"{member.name} ({member.id}) reacted with {emoji}")
    await message.remove_reaction(emoji, member)

    if access_date_active(member.id):
        message = f"{member.name} ({member.id}) already has access to the {PAID_ROLE} Discord Role!"
        logging.info(message)
        await member.send(message)
        return

    url = get_payment_link(member)
    await member.send(
        f"Click the link below to pay for access to the {PAID_ROLE} Discord Role:\n{url}"
    )


@BOT.event
async def on_message(message: discord.Message):
    if (
        not isinstance(message.channel, discord.TextChannel)
        or message.channel.name != PAYMENT_LOGS_CHANNEL
    ):
        return

    try:
        data = {}
        for line in message.content.strip().split("\n"):
            key, value = line.split(": ", 1)
            data[key] = value

        if data.get("event") != "checkout.session.completed":
            return

    except ValueError:
        logging.error("Error parsing message content.")
        return

    store_member(data)

    role = discord.utils.get(message.guild.roles, name=PAID_ROLE)
    await add_role(
        message.guild.get_member(int(data["discord_id"])),
        message.guild.get_role(role.id),
    )
    logging.info(f"Checkout session completed for {data['discord_id']}")


@BOT.event
async def on_ready():
    logging.info(f"We have logged in as {BOT.user}")
    await listen_to_database()


async def add_role(member: discord.Member, role: discord.Role):
    channel = discord.utils.get(role.guild.channels, name=ROLE_LOGS_CHANNEL)
    await member.add_roles(role)

    message = f"Successfully gave the role <@&{role.id}> to <@{member.id}>"
    logging.info(message)
    await channel.send(message)


async def remove_role(member: discord.Member, role: discord.Role):
    channel = discord.utils.get(role.guild.channels, name=ROLE_LOGS_CHANNEL)
    await member.remove_roles(role)

    message = f"Successfully removed the role <@&{role.id}> from <@{member.id}>"
    logging.info(message)
    await channel.send(message)


async def remove_roles_from_expired_members(expired_member_discord_ids: list[str]):
    guild = BOT.get_guild(int(os.getenv("GUILD_ID")))
    role = discord.utils.get(guild.roles, name=PAID_ROLE)

    logging.info(
        f"Removing roles from {len(expired_member_discord_ids)} expired members..."
    )
    for discord_id in expired_member_discord_ids:
        member = guild.get_member(int(discord_id))
        if member is None:
            continue

        await remove_role(member, role)


def handle_snapshot(doc_snapshot, changes, read_time):
    global FIRST_CALL
    if FIRST_CALL:
        FIRST_CALL = False
        return

    logging.info("Received document snapshot after change.")
    BOT.loop.create_task(
        remove_roles_from_expired_members(get_recently_expired_members())
    )


async def listen_to_database():
    logging.info("Listening to database changes...")
    firestore.Client().collection("recently_deleted_customers").document(
        "customer_list"
    ).on_snapshot(handle_snapshot)


def start_bot():
    logging.info("Starting BOT...")
    setup_environment()
    BOT.run(os.getenv("DISCORD_KEY"))
