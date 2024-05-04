import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from .checkout_session import get_payment_link, PAID_ROLE
from .database import get_paid_users

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Bot(command_prefix="!", intents=intents)

# async def add_role(
#     channel: discord.Message.channel, member: discord.Member, role: discord.Role
# ):
#     await member.add_roles(role)
#     await channel.send(f"Successfully gave the role {role.name} to {member.name}")


# async def remove_role(
#     channel: discord.Message.channel, member: discord.Member, role: discord.Role
# ):
#     await member.remove_roles(role)
#     await channel.send(f"Successfully removed the role {role.name} from {member.name}")


@client.event
async def on_message(message):
    print(f"{message.author}: {message.content}")
    x = message.id
    print(x)
    # if message.content == "!pay" or message.content == "!subscribe":
    #     if message.author in get_paid_users():
    #         await message.channel.send(
    #             "You have already paid for access to the channel"
    #         )
    #         return

    #     url = get_payment_link(message.author, message.content == "!subscribe")
    #     thread = await message.create_thread(name=f"Payment - {message.author.name}", auto_archive_duration=60)
    #     await thread.send(
    #         f"Click the link below to pay for access to the {PAID_ROLE} Discord Role:\n{url}"
    #     )


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


def start_bouncer():
    load_dotenv(override=True)
    client.run(os.getenv("DISCORD_KEY"))
