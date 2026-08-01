import httpx
import discord
from discord.ext import commands

class PiStatus(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.api_client = client.api_client

    @commands.is_owner()
    @commands.command(
        name="pi-status",
        help="Checking Status of Mac's RaspiPi"
    )

    async def pi_status(self, ctx):
        response = await self.api_client.get("http://localhost:5000/pi_status")
        data = response.json()
        temp = data["temperatur"]
        storage = data["storage"]

        await ctx.send(f"Status: Temp {temp}°C - Storage: {storage} full")

async def setup(client):
    await client.add_cog(PiStatus(client))