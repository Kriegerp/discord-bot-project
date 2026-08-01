import discord
import random
import os
from discord.ext import commands

class CoinFlip(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.choices = ["Head", "Tail"]

    @commands.command(
            name="coinflip",
            help="Play Coinflip"
    )
    async def coinflip(self, ctx):
        result = random.choice(self.choices)
        await ctx.send(f"Result: {result}")

async def setup(client):
    await client.add_cog(CoinFlip(client))
