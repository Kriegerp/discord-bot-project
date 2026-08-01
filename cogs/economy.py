import discord
from discord.ext import commands

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.api_client = client.api_client

    @commands.command(
        name="balance",
        help="Manage your money on this server."
    )

    async def balance(self, ctx):
        try:
            response = await self.api_client.get(f"http://localhost:5000/balance/{ctx.author.id}")
            data = response.json()

            if 'error' in data:
                await ctx.send(f"Error from Backend: {data['error']}")
                return
            
            balance = data['balance']
            await ctx.send(f"Your balance: {balance}")
        except Exception as e:
            await ctx.send(f"Query error: {type(e).__name__}")

    @commands.command(
        name="daily",
        help="Claim your daily coins."
    )
    async def daily(self, ctx):
        try:
            response = await self.api_client.get(f"http://localhost:5000/daily/{ctx.author.id}")
            data = response.json()

            if 'error' in data:
                await ctx.send(f"Error from Backend: {data['error']}")
                return
            await ctx.send(data['message'])
        
        except Exception as e:
            await ctx.send(f"Query error: {type(e).__name__}")
    
    @commands.command(
        name="pay",
        help="Send money to an user."
    )
    async def pay(self, ctx, target: discord.Member, amount: int):
        if target == ctx.author:
            return await ctx.send("Error: You take your money from your bank and pay it back to your bank.... congrats?")
        
        if amount <= 0:
            return await ctx.send("Error: The amount must be greater than zero.")
        

        try:
            response = await self.api_client.get(f"http://localhost:5000/balance/{ctx.author.id}")
            data = response.json()

            if 'error' in data:
                await ctx.send(f"Error from Backend: {data['error']}")
                return
            
            sender_balance = data.get('balance', 0)

            if sender_balance < amount:
                return await ctx.send(f"Error: Not enough fund! Balance: {sender_balance} coins.")
            
            await ctx.send(f"Sending {amount} coins to {target.display_name}...")
            await self.api_client.post(f"http://localhost:5000/economy/update/{ctx.author.id}", json={"amount": -amount})
            await self.api_client.post(f"http://localhost:5000/economy/update/{target.id}", json={"amount": amount})
            await ctx.send("Success!")
        
        except Exception as e:
            await ctx.send(f"Bank system is down: {e}")

async def setup(client):
    await client.add_cog(Economy(client))