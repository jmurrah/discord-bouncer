import asyncio
import logging
import os

import discord
from google.cloud import firestore

from .checkout_session import PAID_ROLE, get_payment_link
from .database import (access_date_active, delete_expired_users,
                       get_recently_expired_users, store_user)
from .setup import setup_environment

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = discord.Bot(command_prefix="!", intents=intents)

REACTION_CHANNEL = "get-trusted-role"
PAYMENT_LOGS_CHANNEL = "payment-logs"
ROLE_LOGS_CHANNEL = "role-logs"


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    channel = bot.get_channel(payload.channel_id)
    if not isinstance(channel, discord.TextChannel) or channel.name != REACTION_CHANNEL:
        return

    message = await channel.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    emoji = payload.emoji.name

    logging.info(f"{user.name} reacted with {emoji}")
    await message.remove_reaction(emoji, user)

    if emoji == "🧪":
        delete_expired_users()
        return

    if emoji not in ["🪃", "💸"]:
        return

    if access_date_active(user.id):
        logging.info(f"{user.name} already has access to the {PAID_ROLE} Discord Role!")
        await channel.send(
            f"User {user.name} has already paid for access to the {PAID_ROLE} Discord Role!"
        )
        return

    payment_type = "subscribe" if emoji == "🪃" else "pay"
    url = get_payment_link(user, emoji == "🪃")
    await user.send(
        f"Click the link below to {payment_type} for access to the {PAID_ROLE} Discord Role:\n{url}"
    )


@bot.event
async def on_message(message: discord.Message):
    if (
        message.author == bot.user
        or not isinstance(message.channel, discord.TextChannel)
        or message.channel.name != PAYMENT_LOGS_CHANNEL
    ):
        return

    try:
        data = {}
        for line in message.content.strip().split("\n"):
            key, value = line.split(": ", 1)
            data[key] = value
    except ValueError:
        return

    if data["event"] == "checkout.session.completed":
        role = discord.utils.get(message.guild.roles, name=PAID_ROLE)
        store_user(data)
        await add_role(
            message.guild.get_member(int(data["discord_id"])),
            message.guild.get_role(role.id),
        )


@bot.event
async def on_ready():
    logging.info(f"We have logged in as {bot.user}")


async def add_role(member: discord.Member, role: discord.Role):
    channel = discord.utils.get(role.guild.channels, name=ROLE_LOGS_CHANNEL)
    await member.add_roles(role)

    logging.info(f"Successfully gave the role {role.name} to {member.name}")
    await channel.send(f"Successfully gave the role {role.name} to {member.name}")


async def remove_role(member: discord.Member, role: discord.Role):
    channel = discord.utils.get(role.guild.channels, name=ROLE_LOGS_CHANNEL)
    await member.remove_roles(role)

    logging.info(f"Successfully removed the role {role.name} from {member.name}")
    await channel.send(f"Successfully removed the role {role.name} from {member.name}")


async def remove_roles_from_expired_users(expired_users: list[str]):
    guild = bot.guilds[0]
    role = discord.utils.get(guild.roles, name=PAID_ROLE)

    logging.info(f"Removing roles from {len(expired_users)} expired users...")
    for discord_id in expired_users:
        member = guild.get_member(int(discord_id))
        if member is None:
            continue

        await remove_role(member, role)


def handle_snapshot(doc_snapshot, changes, read_time):
    logging.info("Received document snapshot after change")
    bot.loop.create_task(remove_roles_from_expired_users(get_recently_expired_users()))


async def listen_to_database():
    logging.info("Listening to database changes...")
    firestore.Client().collection("recently_deleted_customers").document(
        "customer_list"
    ).on_snapshot(handle_snapshot)


def start_bot():
    setup_environment()
    asyncio.run(listen_to_database())
    bot.run(os.getenv("DISCORD_KEY"))
