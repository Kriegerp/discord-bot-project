import discord
import os
from dotenv import load_dotenv
import random
import time
from discord.ext import commands, tasks
import asyncio
import httpx

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

OWNER_ID = int(os.environ.get('OWNER_ID'))
IMAGE_CHANNEL_ID = int(os.environ.get('IMAGE_CHANNEL_ID'))

client = commands.Bot(command_prefix = "!", intents = intents, owner_id=OWNER_ID)

client.api_client = httpx.AsyncClient()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    if not images.is_running():
        images.start()
        print("Image loop gestartet.")


@tasks.loop(seconds=21600)
async def images():
    try:
        channel = client.get_channel(IMAGE_CHANNEL_ID)
        script_dir = os.path.abspath(os.path.dirname(__file__))     #Get script directory
        images_dir = os.path.join(script_dir, "images")              #Get all files from images directory

        filenames = os.listdir(images_dir)
        extensions = ('.png','.jpg','.gif')                         #Allowed file extensions
        images_list = []

        for i in filenames:                                         #Check if files have supported extensions
            if i.endswith(extensions) and i not in images_list:
                images_list.append(i)
        if not images_list:
            print("Keine Bilder im 'images'-Ordner gefunden.")
            return

        random_img_name = random.choice(images_list)
        random_img_path = os.path.join(images_dir, random_img_name)

        await channel.send(file=discord.File(random_img_path))
    except Exception as e:
        print(f"Fehler im 'images' loop: {e}")

async def load_cogs():
    try:
        await client.load_extension('cogs.ping')
        print("Ping Cog geladen.")
    except Exception as e:
        print(f"Fehler beim Laden von cogs.ping: {e}")

    try:
        await client.load_extension('cogs.magic8balls')
        print("Magic8Ball Cog geladen.")
    except Exception as e:
        print(f"Fehler beim Laden von cogs.magic8balls: {e}")
    
    try:
        await client.load_extension('cogs.arts')
        print("Arts Cog geladen.")
    except Exception as e:
        print(f"Fehler beim Laden von cogs.arts: {e}")

    try:
        await client.load_extension('cogs.coinflip')
        print("Coinflip geladen.")
    except Exception as e:
        print(f"Fehler beim Laden von cogs.coinflip: {e}")

    try:
        await client.load_extension('cogs.pi-status')
        print("Pi-Status geladen.")
    except Exception as e:
        print(f"Fehler beim Laden von cogs.pi-status: {e}")

    try:
        await client.load_extension('cogs.economy')
        print("Economy geladen.")
    except Exception as e:
        print(f"Fehler beim Laden von cogs.economy: {e}")

    try:
        await client.load_extension('cogs.dice')
        print("Dice geladen.")
    except Exception as e:
        print(f"Fehler beim Laden von cogs.dice: {e}")

    try:
        await client.load_extension('cogs.oc')
        print("OC geladen.")
    except Exception as e:
        print(f"Fehler beim Laden von cogs.oc: {e}")

    try:
        await client.load_extension('cogs.economy_games')
        print("Blackjack geladen")
    except Exception as e:
        print(f"Fehler beim Laden von cogs.economy_games: {e}")


async def main():
    async with client:
        await load_cogs()
        BOT_TOKEN = os.environ.get('DISCORD_TOKEN')
        await client.start(BOT_TOKEN)

if __name__ == "__main__":
    script_dir = os.path.abspath(os.path.dirname(__file__))
    images_dir = os.path.join(script_dir, "images")
    asyncio.run(main())
