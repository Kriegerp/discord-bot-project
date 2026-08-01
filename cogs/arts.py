import discord
import random
import os
from discord.ext import commands

class ArtCog(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    # 2. Das hier ist der neue Befehl!
    #    Der Bot wird jetzt auf "!dmc_art" reagieren.
    @commands.command()
    async def dmc_art(self, ctx):
        try:
            # 1. Finde den Bilder-Ordner (genau wie im Loop)
            script_dir = os.path.abspath(os.path.dirname(__file__))
            # WICHTIG: Wir sind im 'cogs'-Ordner, also müssen wir
            # eine Ebene 'raus' (../) um zum 'images'-Ordner zu kommen
            images_dir = os.path.join(script_dir, "..", "images") 

            # 2. Lade alle Dateinamen (genau wie im Loop)
            filenames = os.listdir(images_dir)
            extensions = ('.png', '.jpg', '.gif')
            
            images_list = []
            for i in filenames:
                if i.endswith(extensions) and i not in images_list:
                    images_list.append(i)

            if not images_list:
                await ctx.send("Sorry, image not found.")
                return

            # 3. Wähle ein Bild aus und baue den Pfad (genau wie im Loop)
            random_img_name = random.choice(images_list)
            random_img_path = os.path.join(images_dir, random_img_name) 

            # 4. Sende das Bild als Antwort auf den Befehl
            await ctx.send(file=discord.File(random_img_path))
        
        except Exception as e:
            print(f"Fehler im 'dmc_art' Befehl: {e}")
            await ctx.send("Error, something went wrong.")


# 3. Die setup-Funktion, die den Cog lädt.
#    Wichtig: Sie muss auf die neue Klasse 'ArtCog' verweisen.
async def setup(client):
    await client.add_cog(ArtCog(client))