import discord
import random
import os
from discord.ext import commands

# token = os.environ["M8B_DISCORD_TOKEN"]
# client = discord.Client()

class Magic8Ball(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.response_list = ['It is certain',
            'It is decidedly so',
            'Yes, definitely',
            'Reply hazy, try again',
            'Ask again later',
            'Concentrate and ask again',
            'My reply is no',
            'Outlook not so good',
            'Very doubtful'
        ]

    @commands.command(
            name="m8b",
            help="Answers your question somehow."
    )
    async def magic_eight_ball(self, ctx, *, question: str = None):

        if question is None:
            await ctx.send("You didn't ask something!")
            return
        
        lucky_num = random.randint(0,len(self.response_list) - 1)
        await ctx.send(f"> {question}\n:8ball: {self.response_list[lucky_num]}")

async def setup(client):
    await client.add_cog(Magic8Ball(client))
