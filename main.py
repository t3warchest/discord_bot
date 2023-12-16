
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

client = commands.Bot(command_prefix="!",intents=discord.Intents.all())

@client.event
async def on_ready():
    print("### Ready ###")

@client.command()
async def hello(ctx):
    await ctx.send("Hello World")
    
    server_name = ctx.guild.name
    
    print(f"Hello World {server_name}")
    


client.run(os.getenv('TOKEN'))