import discord
from dotenv import load_dotenv
import os
from .checkout_session import get_payment_link, PAID_ROLE
from .database import is_paid_user
import logging


logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = discord.Bot(command_prefix="!", intents=intents)


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


@bot.event
async def on_message(message):
    logging.info(f"{message.author}: {message.content}")

    if message.content == "!pay" or message.content == "!subscribe":
        if is_paid_user(message.author.id):
            await message.channel.send(
                f"You have already paid for access to the {PAID_ROLE} Discord Role!"
            )
            return

        url = get_payment_link(message.author, message.content == "!subscribe")
        thread = await message.create_thread(
            name=f"Payment - {message.author.name}", auto_archive_duration=60
        )
        await thread.send(
            f"Click the link below to pay for access to the {PAID_ROLE} Discord Role:\n{url}"
        )


@bot.event
async def on_ready():
    logging.info(f"We have logged in as {bot.user}")


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

        os.environ[secret_name] = secret_value


def start_bouncer():
    # load_secrets_into_env()
    load_dotenv(override=True)
    bot.run(os.getenv("DISCORD_KEY"))
