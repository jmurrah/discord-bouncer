import logging

import discord

from .checkout_session import PAID_ROLE, get_payment_link
from .scheduler import get_expired_users, user_has_paid

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = discord.Bot(command_prefix="!", intents=intents)

REACTION_CHANNEL = "get-trusted-role"
PAYMENT_LOGS_CHANNEL = "payment-logs"


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

    if user_has_paid(user.id):
        await channel.send(
            f"You have already paid for access to the {PAID_ROLE} Discord Role!"
        )
        return

    if emoji in ["🪃", "💸"]:
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

    data = {}
    for line in message.content.strip().split("\n"):
        key, value = line.split(": ", 1)
        data[key] = value

    if data["event"] == "checkout.session.completed":
        role = discord.utils.get(message.guild.roles, name=PAID_ROLE)
        await add_role(
            message.channel,
            message.guild.get_member(int(data["discord_id"])),
            message.guild.get_role(role.id),
        )


@bot.event
async def on_ready():
    logging.info(f"We have logged in as {bot.user}")


async def add_role(
    channel: discord.Message.channel, member: discord.Member, role: discord.Role
):
    await member.add_roles(role)
    await channel.send(f"Successfully gave the role {role.name} to {member.name}")


async def remove_role(
    channel: discord.Message.channel, member: discord.Member, role: discord.Role
):
    await member.remove_roles(role)
    await channel.send(f"Successfully removed the role {role.name} from {member.name}")


async def remove_roles_from_expired_users():
    expired_users = get_expired_users()
    guild = bot.guilds[0]
    role = discord.utils.get(guild.roles, name=PAID_ROLE)

    for user_id in expired_users:
        member = guild.get_member(int(user_id))
        if member is None:
            continue

        if user_has_paid(user_id):
            await remove_role(PAYMENT_LOGS_CHANNEL, member, role)
