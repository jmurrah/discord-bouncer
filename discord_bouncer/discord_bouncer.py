import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from .checkout_session import handle_checkout_session
from .database import get_paid_users

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

PAID_ROLE = "secret_chat"


async def add_role(channel: discord.Message.channel, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await channel.send(f"Successfully gave the role {role.name} to {member.name}")


async def remove_role(
    channel: discord.Message.channel, member: discord.Member, role: discord.Role
):
    await member.remove_roles(role)
    await channel.send(f"Successfully removed the role {role.name} from {member.name}")

@client.event
async def on_message(message):
    print(message.content, message.author)
    if message.author == client.user:
        return

    if message.content == "!pay":
        if message.author in get_paid_users():
            await message.channel.send("You have already paid for access to the channel")
            return
        
        url = handle_checkout_session()
        await message.channel.send(f"Click the link below to pay for access to the channel:\n{url}")
    
    if message.content == "!add_role":
        for role in message.guild.roles:
            if role.name == PAID_ROLE:
                await add_role(message.channel, message.author, role)
    
    if message.content == "!remove_role":
        for role in message.guild.roles:
            if role.name == PAID_ROLE:
                await remove_role(message.channel, message.author, role)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


def start_bouncer():
    load_dotenv(override=True)
    client.run(os.getenv("DISCORD_KEY"))
