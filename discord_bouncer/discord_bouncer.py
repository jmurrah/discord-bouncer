import discord
from dotenv import load_dotenv
import os
from .checkout_session import get_payment_link, PAID_ROLE
from .database import user_has_paid
import logging
from google.cloud import secretmanager

logging.basicConfig(level=logging.INFO)

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
        await user.send(f"Click the link below to {payment_type} for access to the {PAID_ROLE} Discord Role:\n{url}")


@bot.event
async def on_message(message: discord.Message):
    if not isinstance(message.channel, discord.TextChannel) or message.channel.name != PAYMENT_LOGS_CHANNEL:
        return
    
    data = {}
    for line in message.content.strip().split("\n"):
        key, value = line.split(": ", 1)
        data[key] = value

    if data["event"] == "checkout.session.completed":
        role = discord.utils.get(message.guild.roles, name=PAID_ROLE)
        add_role(
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


def load_secrets_into_env():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    secrets_manager = secretmanager.SecretManagerServiceClient()
    secrets = secrets_manager.list_secrets(request={"parent": f"projects/{project_id}"})

    for secret in secrets:
        secret_version = secrets_manager.access_secret_version(
            request={"name": f"{secret.name}/versions/latest"}
        )

        secret_value = secret_version.payload.data.decode("UTF-8")
        secret_name = secret.name.split("/")[-1]
        logger.info(f"Setting {secret_name} in environment!")
        os.environ[secret_name] = secret_value


def main():
    # load_secrets_into_env()
    load_dotenv(override=True)
    bot.run(os.getenv("DISCORD_KEY"))
