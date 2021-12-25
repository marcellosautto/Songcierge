# importing discord.py
import discord

# used for reading token from env file
import os 
from dotenv import load_dotenv
load_dotenv(".env")

# establish connection to discord
client = discord.Client()

# print msg when the bot is online
@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))

# The bot will say hello if the '$hello' command is executed
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

# run bot with login token
client.run(os.getenv('TOKEN'))