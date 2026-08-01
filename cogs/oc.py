import discord
from discord.ext import commands
import httpx

class OCs(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.api_client = client.api_client

    @commands.group(
            name="oc",
            help="Mac's OCs. !oc <name> to show",
            invoke_without_command=True
    )
    async def oc_group(self, ctx, name: str = None):
        # Hauptgruppe für OC-Befehle

        # Shows info on !oc <name>
        if ctx.invoked_subcommand is None and name is not None:
            print(f"--- [DEBUG] oc_group aufgerufen für: {name} ---") # NEU
            import traceback # NEU: Import für detaillierte Fehler
            try:
                # calls backend-route
                url = f"http://localhost:5000/ocs/get/{name}"
                print(f"--- [DEBUG] Rufe Backend URL auf: {url} ---") # NEU
                response = await self.api_client.get(url)
                print(f"--- [DEBUG] Backend Status Code: {response.status_code} ---") # NEU

                data = response.json()
                print(f"--- [DEBUG] Empfangene Daten: {data} ---") # NEU

                # Checks error of backend (e.g. OC not found)
                if 'error' in data:
                    print(f"--- [DEBUG] Backend meldet Fehler: {data['error']} ---") # NEU
                    await ctx.send(f"Error from Backend: {data['error']}")
                    return

                # creates Embed
                print(f"--- [DEBUG] Erstelle Embed... ---") # NEU
                embed = discord.Embed(
                        title=f"OC profile: {data.get('name', 'N/A')}",
                        description=data.get('description', '*No description set.*'),
                        color=discord.Color.yellow()
                    )
                # Füge Felder hinzu, falls sie nicht None oder leer sind
                if data.get('age'):
                    embed.add_field(name="Age", value=data.get('age'), inline=True)
                if data.get('height'):
                    embed.add_field(name="Height", value=data.get('height'), inline=True)

                # Füge das Bild hinzu, falls eine URL vorhanden ist
                if data.get('picture') and data.get('picture') != 'URL': # Ignoriere den Default-Wert
                    embed.set_image(url=data.get('picture'))
                else:
                    embed.set_footer(text="No picture set.") # Kleiner Hinweis
                print(f"--- [DEBUG] Embed erstellt, sende... ---") # NEU
                await ctx.send(embed=embed)
                print(f"--- [DEBUG] Embed gesendet. ---") # NEU

            except Exception as e:
                print(f"!!! [DEBUG] FEHLER im try-Block: {type(e).__name__}: {e}") # NEU
                traceback.print_exc() # Druckt den detaillierten Fehler ins Log

                await ctx.send(f"Konnte OC-Daten nicht abrufen. Fehler: {type(e).__name__}")
            return # Funktion hier beenden nach der Anzeige


        # If user shows only '!oc':
        elif ctx.invoked_subcommand is None and name is None:
            await ctx.send("Please enter a name ('!oc <name>')")

    @commands.is_owner()
    @oc_group.command(
         name="create",
         help="Creates a new OC data"
    )
    async def create_oc(self, ctx, name: str):
            # Creates new OC in database

            # Python-Dictionary
            data_to_send = {"name": name}

            try:
                response = await self.api_client.post(
                    "http://localhost:5000/ocs/create", 
                    json=data_to_send
                )
                data = response.json()
                
                if 'error' in data:
                    await ctx.send(f"Error from Backend: {data['error']}")
                else:
                    await ctx.send(data['message'])

            except Exception as e:
                await ctx.send(f"Couldn't reach Backend. Error: {type(e).__name__}")
    
    @commands.is_owner()
    @oc_group.group(
        name="set",
        help="Sets OC information (e.g. !oc set age <name> <value>)",
        invoke_without_command=True
    )
    async def set_group(self, ctx):
        # Subgroup for setting OC attr

        if ctx.invoked_subcommand is None:
            await ctx.send("Specify what you wanna set")
    
    @set_group.command(name="age")
    async def set_age(self, ctx, name: str, value: int):
        data_to_send = {
            "name": name,
            "field": "age",
            "value": value}

        try:
            response = await self.api_client.post(
                "http://localhost:5000/ocs/update", 
                json=data_to_send
                )
            data = response.json()
                
            if 'error' in data:
                await ctx.send(f"Error from Backend: {data['error']}")
            else:
                await ctx.send(data['message'])

        except Exception as e:
            await ctx.send(f"Couldn't reach Backend. Error: {type(e).__name__}")
            
    @commands.is_owner()
    @set_group.command(name="height")
    async def set_height(self, ctx, name: str, value: str):
        data_to_send = {
            "name": name,
            "field": "height",
            "value": value
        }

        try:
            response = await self.api_client.post(
                "http://localhost:5000/ocs/update", 
                json=data_to_send
                )
            data = response.json()
                
            if 'error' in data:
                await ctx.send(f"Error from Backend: {data['error']}")
            else:
                await ctx.send(data['message'])

        except Exception as e:
            await ctx.send(f"Couldn't reach Backend. Error: {type(e).__name__}")

    @commands.is_owner()
    @set_group.command(name="description")
    async def set_description(self, ctx, name: str, *, value: str):
        data_to_send = {
            "name": name,
            "field": "description",
            "value": value
        }

        try:
            response = await self.api_client.post(
                "http://localhost:5000/ocs/update", 
                json=data_to_send
            )
            data = response.json()
                
            if 'error' in data:
                await ctx.send(f"Error from Backend: {data['error']}")
            else:
                await ctx.send(data['message'])

        except Exception as e:
            await ctx.send(f"Couldn't reach Backend. Error: {type(e).__name__}")

    @commands.is_owner()
    @set_group.command(name="picture")
    async def set_picture(self, ctx, name: str, value: str):
        data_to_send = {
            "name": name,
            "field": "picture",
            "value": value
        }

        try:
            response = await self.api_client.post(
                "http://localhost:5000/ocs/update", 
                json=data_to_send
            )
            data = response.json()
                
            if 'error' in data:
                await ctx.send(f"Error from Backend: {data['error']}")
            else:
                await ctx.send(data['message'])

        except Exception as e:
            await ctx.send(f"Couldn't reach Backend. Error: {type(e).__name__}")

    @commands.is_owner()
    @oc_group.command(
        name="delete",
        help="Deletes an existing OC data"
    )
    async def delete_oc(self, ctx, name: str):
        # Delete an OC in database

        try:
            response = await self.api_client.delete(f"http://localhost:5000/ocs/delete/{name}")
            data = response.json()
            
            if 'error' in data:
                    await ctx.send(f"Error from Backend: {data['error']}")
            else:
                    await ctx.send(data['message'])

        except Exception as e:
            await ctx.send(f"Couldn't reach Backend. Error: {type(e).__name__}")

    @oc_group.command(
        name="list",
        help="Lists all OCs"
    )
    async def list_all_oc(self, ctx):
        # Lists all OCs from database

        try:
            response = await self.api_client.get(f"http://localhost:5000/ocs/list/")
            data = response.json()
            
            if 'error' in data:
                await ctx.send(f"Error from Backend: {data['error']}")
                return
            
            if 'names' in data and data['names']:
                name_string = '\n'.join(data['names'])
                await ctx.send(f"All OCs:\n{name_string}")
            else:
                await ctx.send("Empty list")

        except Exception as e:
            await ctx.send(f"Couldn't reach Backend. Error: {type(e).__name__}")
              

async def setup(client):
    await client.add_cog(OCs(client))
