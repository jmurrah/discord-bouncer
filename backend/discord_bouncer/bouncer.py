import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

client = discord.Client(intents=discord.Intents.default())


async def add_role(context: commands.Context, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await context.send(f"Successfully gave the role {role.name} to {member.name}")


async def remove_role(
    context: commands.Context, member: discord.Member, role: discord.Role
):
    await member.remove_roles(role)
    await context.send(f"Successfully removed the role {role.name} from {member.name}")


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


def start_bouncer():
    load_dotenv()
    client.run(os.getenv("DISCORD_KEY"))
    breakpoint()
