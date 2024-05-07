import discord
from dotenv import load_dotenv
import os
from .checkout_session import get_payment_link, PAID_ROLE
from .database import is_paid_user
import logging
from google.cloud import secretmanager

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = discord.Bot(command_prefix="!", intents=intents)

REACTION_CHANNEL = "get-trusted-role"


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    channel = bot.get_channel(payload.channel_id)
    if not isinstance(channel, discord.TextChannel) or channel.name != REACTION_CHANNEL:
        return

    message = await channel.fetch_message(payload.message_id)
    user = bot.get_user(payload.user_id)
    emoji = payload.emoji.name

    logging.info(f"{user.name} reacted with {emoji}")
    print(f"{user.name} reacted with: {emoji}")

    await message.remove_reaction(emoji, user)


    if is_paid_user(user.id):
        await channel.send(
            f"You have already paid for access to the {PAID_ROLE} Discord Role!"
        )
        return
    
    if emoji in ["🪃", "💸"]:
        url = get_payment_link(user, emoji == "🪃")
        if emoji == "🪃":
            await user.send(f"Click the link below to subscribe for access to the {PAID_ROLE} Discord Role:\n{url}")
        else:
            await user.send(f"Click the link below to pay for access to the {PAID_ROLE} Discord Role:\n{url}")


@bot.event
async def on_ready():
    logging.info(f"We have logged in as {bot.user}")
    print(f"We have logged in as {bot.user}")


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
        print(f"Setting {secret_name} in environment!")
        os.environ[secret_name] = secret_value


def main():
    # load_secrets_into_env()
    load_dotenv(override=True)
    bot.run(os.getenv("DISCORD_KEY"))
