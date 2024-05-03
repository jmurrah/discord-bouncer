import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from .stripe import create_checkout_session

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)


# async def add_role(context: commands.Context, member: discord.Member, role: discord.Role):
#     await member.add_roles(role)
#     await context.send(f"Successfully gave the role {role.name} to {member.name}")


# async def remove_role(
#     context: commands.Context, member: discord.Member, role: discord.Role
# ):
#     await member.remove_roles(role)
#     await context.send(f"Successfully removed the role {role.name} from {member.name}")

@client.event
async def on_message(message):
    print(message.content)
    if message.author == client.user:
        return

    if message.content == "!payment":
        #check DB to see if the user has already paid/if a link is open
        url = create_checkout_session()
        print(url)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


def start_bouncer():
    load_dotenv(override=True)
    client.run(os.getenv("DISCORD_KEY"))
