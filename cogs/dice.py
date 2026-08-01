import discord
import random
import os
from discord.ext import commands

class DiceCog(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.amount = 1
        self.sides = 20

    @commands.command(
            name="roll",
            help="Roll a dice. e.g. !roll 2d6 for 2 Dices with 6 sides."
    )
    async def roll(self, ctx, input: str = None):

        count = 0
        sides = 0
        
        # just !roll
        if input == None:
            count = self.amount
            sides = self.sides

            roll = random.randint(1, sides)

            await ctx.send(f"Result for 1d20: {roll}")
            return
        
        # !roll with something as argument
        # no 'd' in argument
        if 'd' not in input:
            await ctx.send("Jesse, what the f*** are you talking about? d20, you understand? d20!!")
            return

        # too many 'd's
        if input.count('d') > 1:
            await ctx.send("Too many d's. Proper usage: !roll d20 or !roll 4d8.")
            return
    
        input_list = input.split("d")
        count_str = input_list[0]
        sides_str = input_list[1]

        # Checking Count
        if count_str == '':
            count = self.amount # Standard 1
        elif count_str.isdigit():
            count = int(count_str)
            if count > 30:
                await ctx.send("The number is too high, choose lesser than 30, please")
                return
        else: # e.g. "adb"
            await ctx.send(f"What is this letter '{count_str}', huh? I know only numbers >:(")
            return
        
        # Checking Sides
        if sides_str == '':
            sides = self.sides # Standard 20
        elif sides_str.isdigit():
            sides = int(sides_str)
            if sides > 100:
                await ctx.send("The number is too high, choose lesser than 100, please")
                return
        else:
            # e.g. "4dG"
            await ctx.send(f"Oh wow look at this '{sides_str}'! Not even a number!")
            return
        
        sum = 0
        add_list = []
        for i in range(count):
            add = random.randint(1, sides)
            add_list.append(add)
            sum += add

        await ctx.send(f"Result for {count}d{sides}: {sum} with {count} dice(s) consisting of {add_list}")

async def setup(client):
    await client.add_cog(DiceCog(client))
