import discord
from discord.ext import commands
import random
import asyncio

class RideTheBusView(discord.ui.View):
    def __init__(self, ctx, bet, api_client):
        super().__init__(timeout=60.0)
        self.ctx = ctx
        self.bet = bet
        self.api_client = api_client
        self.multiplier = 1
        self.phase = 1
        self.card_history = []
        
        self.values = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
        self.suits = ["♥️", "♦️", "♠️", "♣️"]
        
        # Beim Start sofort prüfen, welche Knöpfe an sein dürfen
        self.update_buttons()

    def draw_card(self):
        while True:
            # 1. Wir ziehen eine zufällige Karte
            rank = random.choice(list(self.values.keys()))
            suit = random.choice(self.suits)
            
            # 2. Wir prüfen: Liegt diese exakte Karte schon auf dem Tisch (im Rucksack)?
            if (rank, suit) not in self.card_history:
                # 3. Wenn NEIN, geben wir sie zurück. Die Schleife endet sofort!
                return rank, suit
            
            # Wenn JA, geht die Schleife unsichtbar und blitzschnell von vorne los, 
            # solange bis wir eine frische Karte gefunden haben. Der User merkt davon nichts!

    def update_buttons(self):
        # 1. Wir machen pauschal ALLE Knöpfe auf dem Tablet aus
        for child in self.children:
            child.disabled = True

        # 2. Wenn das Spiel vorbei ist (Phase 99), bleiben alle aus. Wir sind fertig!
        if self.phase == 99 or self.phase == 5:
            return

        # 3. Wir schalten NUR die Knöpfe an, die zur aktuellen Phase passen!
        for child in self.children:
            if self.phase == 1 and child.label in ["Red", "Black"]:
                child.disabled = False
            elif self.phase == 2 and child.label in ["Higher", "Lower"]:
                child.disabled = False
            elif self.phase == 3 and child.label in ["Inside", "Outside"]:
                child.disabled = False
            elif self.phase == 4 and child.label in ["♥️", "♦️", "♠️", "♣️"]:
                child.disabled = False
    
    def get_game_text(self, status_msg="**Ride the Bus - Phase 1: Red or Black?**"):
        # Wir bauen einen String, der alle bisherigen Karten anzeigt
        cards_str = " ".join([f"**{r}{s}**" for r, s in self.card_history]) if self.card_history else "*None*"
        
        return (
            f"🚌 **Ride The Bus** | Player: {self.ctx.author.display_name}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{status_msg}\n\n"
            f"Your Cards: {cards_str}\n"
            f"Current Multiplicator: **x{self.multiplier}**\n"
            f"Potential Pot: **{int(self.bet * self.multiplier)}** coins"
        )

    # ================= ROW 0 =================
    @discord.ui.button(label="Red", style=discord.ButtonStyle.red, emoji="🔴", row=0)
    async def button_red(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Shoo, it's not your game!", ephemeral=True)

        next_rank, next_suit = self.draw_card()

        self.card_history.append((next_rank, next_suit))

        if next_suit in ["♥️", "♦️"]:
            self.multiplier *= 2
            self.phase += 1
            self.update_buttons()
            await interaction.response.edit_message(content=self.get_game_text("Correct! Phase 2: **Higher or Lower?**"), view=self)
        else:
            self.phase = 99
            self.update_buttons()
            await interaction.response.edit_message(content=self.get_game_text(f"**Bust!** It was Black. {self.ctx.author.display_name} lost {self.bet} coins."), view=self)
            self.stop()

    @discord.ui.button(label="Black", style=discord.ButtonStyle.grey, emoji="⚫", row=0)
    async def button_black(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Shoo, it's not your game!", ephemeral=True)

        next_rank, next_suit = self.draw_card()

        self.card_history.append((next_rank, next_suit))

        if next_suit in ["♠️", "♣️"]:
            self.multiplier *= 2
            self.phase += 1
            self.update_buttons()
            await interaction.response.edit_message(content=self.get_game_text("Correct! Phase 2: **Is next card higher or lower?**"), view=self)
        else:
            self.phase = 99
            self.update_buttons()
            await interaction.response.edit_message(content=self.get_game_text(f"**Bust!** It was Red. {self.ctx.author.display_name} lost {self.bet} coins."), view=self)
            self.stop()

    @discord.ui.button(label="Higher", style=discord.ButtonStyle.green, emoji="⬆️", row=0)
    async def button_higher(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Shoo, it's not your game!", ephemeral=True)
        
        next_rank, next_suit = self.draw_card()
        self.card_history.append((next_rank, next_suit))

        if self.values[next_rank] > self.values[self.card_history[0][0]]:
            self.multiplier *= 2
            self.phase += 1
            self.update_buttons()
            await interaction.response.edit_message(content=self.get_game_text("Correct! Phase 3: **Is next card's value inside or outside of your first and second card?**"), view=self)
        else:
            self.phase = 99
            self.update_buttons()
            await interaction.response.edit_message(content=self.get_game_text(f"**Bust!** {self.ctx.author.display_name} lost {self.bet} coins."), view=self)
            self.stop()

    @discord.ui.button(label="Lower", style=discord.ButtonStyle.red, emoji="⬇️", row=0)
    async def button_lower(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Shoo, it's not your game!", ephemeral=True)
        
        next_rank, next_suit = self.draw_card()
        self.card_history.append((next_rank, next_suit))

        if self.values[next_rank] < self.values[self.card_history[0][0]]:
            self.multiplier *= 2
            self.phase += 1
            self.update_buttons()
            await interaction.response.edit_message(content=self.get_game_text("Correct! Phase 3: **Is next card's value inside or outside of your first and second card?**"), view=self)
        else:
            self.phase = 99
            self.update_buttons()
            await interaction.response.edit_message(content=self.get_game_text(f"**Bust!** {self.ctx.author.display_name} lost {self.bet} coins."), view=self)
            self.stop()

    # ================= ROW 1 =================        
    @discord.ui.button(label="Inside", style=discord.ButtonStyle.blurple, emoji="🏠", row=1)
    async def button_inside(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Shoo, it's not your game!", ephemeral=True)

        next_rank, next_suit = self.draw_card()
        self.card_history.append((next_rank, next_suit))

        # Wir holen uns die Werte als Zahlen:
        val1 = self.values[self.card_history[0][0]]
        val2 = self.values[self.card_history[1][0]]
        next_val = self.values[next_rank]

        # Wir finden die Grenzen:
        untere_grenze = min(val1, val2)
        obere_grenze = max(val1, val2)

        # Check: next_val größer als untere_grenze und kleiner als obere_grenze
        if untere_grenze < next_val < obere_grenze:
            self.multiplier *= 2
            self.phase += 1
            self.update_buttons()
            await interaction.response.edit_message(content=self.get_game_text("Correct! Final Phase: **Guess the suit of final card!**"), view=self)
        else:
            self.phase = 99
            self.update_buttons()
            await interaction.response.edit_message(content=self.get_game_text(f"**Bust!** {self.ctx.author.display_name} lost {self.bet} coins."), view=self)
            self.stop()

    @discord.ui.button(label="Outside", style=discord.ButtonStyle.green, emoji="🏕️", row=1)
    async def button_outside(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Shoo, it's not your game!", ephemeral=True)

        next_rank, next_suit = self.draw_card()
        self.card_history.append((next_rank, next_suit))

        # Wir holen uns die Werte als Zahlen:
        val1 = self.values[self.card_history[0][0]]
        val2 = self.values[self.card_history[1][0]]
        next_val = self.values[next_rank]

        # Wir finden die Grenzen:
        untere_grenze = min(val1, val2)
        obere_grenze = max(val1, val2)

        # Check: next_val größer als untere_grenze und kleiner als obere_grenze
        if next_val < untere_grenze or next_val > obere_grenze:
            self.multiplier *= 2
            self.phase += 1
            self.update_buttons()
            await interaction.response.edit_message(content=self.get_game_text("Correct! Final Phase: **Guess the Suit!**"), view=self)
        else:
            self.phase = 99
            self.update_buttons()
            await interaction.response.edit_message(content=self.get_game_text(f"**Bust!** {self.ctx.author.display_name} lost {self.bet} coins."), view=self)
            self.stop()

    # ================= ROW 2 =================  
    @discord.ui.button(label="♥️", style=discord.ButtonStyle.red, row=2)
    async def button_heart(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_suit_guess(interaction, "♥️")

    @discord.ui.button(label="♦️", style=discord.ButtonStyle.red, row=2)
    async def button_diamond(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_suit_guess(interaction, "♦️")

    @discord.ui.button(label="♠️", style=discord.ButtonStyle.gray, row=2)
    async def button_spade(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_suit_guess(interaction, "♠️")

    @discord.ui.button(label="♣️", style=discord.ButtonStyle.gray, row=2)
    async def button_club(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_suit_guess(interaction, "♣️")

    # Hilfsfunktion für das Finale, spart 4x Copy-Paste!
    async def handle_suit_guess(self, interaction: discord.Interaction, guessed_suit: str):
        if interaction.user.id != self.ctx.author.id: return await interaction.response.send_message("Shoo!", ephemeral=True)
        next_rank, next_suit = self.draw_card()
        self.card_history.append((next_rank, next_suit))

        if next_suit == guessed_suit:
            self.multiplier *= 2; self.phase = 5; self.update_buttons()
            final_win = int(self.bet * self.multiplier)
            await self.api_client.post(f"http://localhost:5000/economy/update/{self.ctx.author.id}", json={"amount": final_win})
            await interaction.response.edit_message(content=self.get_game_text(f"**JACKPOT!** You survived the bus and won **{final_win} coins**!"), view=self)
            self.stop()
        else:
            self.phase = 99; self.update_buttons()
            await interaction.response.edit_message(content=self.get_game_text(f"**Bust!** It was {next_suit}. {self.ctx.author.display_name} lost {self.bet} coins."), view=self)
            self.stop()


class HighLowView(discord.ui.View):
    def __init__(self, ctx, bet, api_client):
        super().__init__(timeout=45.0)
        self.ctx = ctx
        self.bet = bet
        self.api_client = api_client
        self.multiplier = 1
        self.streak = 0
        
        self.values = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
        self.suits = ["♥️", "♦️", "♠️", "♣️"]
        self.current_rank, self.current_suit = self.draw_card()

    def draw_card(self):
        rank = random.choice(list(self.values.keys()))
        suit = random.choice(self.suits)
        return rank, suit

    def get_game_text(self, status_msg="**High-Low Start!**"):
        return (
            f"👤 **Player:** {self.ctx.author.display_name}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{status_msg}\n"
            f"Your card: **{self.current_rank}{self.current_suit}**\n"
            f"Multiplicator: **x{self.multiplier}** | Streak: **{self.streak}**\n"
            f"Current Pot: **{int(self.bet * self.multiplier)}** coins\n\n"
            f"Is the next card higher or lower?"
        )

    @discord.ui.button(label="Higher", style=discord.ButtonStyle.green, emoji="⬆️")
    async def button_higher(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Shoo, it's not your game!", ephemeral=True)

        next_rank, next_suit = self.draw_card()

        if self.values[next_rank] == self.values[self.current_rank]:
            self.current_rank, self.current_suit = next_rank, next_suit
            await interaction.response.edit_message(content=self.get_game_text(f"**Tie!** Both were {next_rank}. No risk!"), view=self)
            return

        if self.values[next_rank] > self.values[self.current_rank]:
            self.multiplier += 1
            self.streak += 1

            if self.streak % 5 == 0:
                self.multiplier *= 2
                msg = f"**Streak Bonus!** Multiplicator has been doubled. It was {next_rank}{next_suit}."
            else:
                msg = f"**Correct!** It was {next_rank}{next_suit}."

            self.current_rank, self.current_suit = next_rank, next_suit

            # Cash Out Knopf anschalten
            for child in self.children:
                if child.label == "Cash Out":
                    child.disabled = False
                    
            # WICHTIG: Das view=self MUSS hierhin, sonst bleibt der Knopf aus!
            await interaction.response.edit_message(content=self.get_game_text(msg), view=self)
            
        else: # (Das ist der Verlust)
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(content=f"**{self.ctx.author.display_name} busted!** The card was **{next_rank}{next_suit}**. You lost {self.bet} coins.", view=self)
            self.stop()

    @discord.ui.button(label="Lower", style=discord.ButtonStyle.red, emoji="⬇️")
    async def button_lower(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Shoo, it's not your game!", ephemeral=True)

        next_rank, next_suit = self.draw_card()

        if self.values[next_rank] == self.values[self.current_rank]:
            self.current_rank, self.current_suit = next_rank, next_suit
            await interaction.response.edit_message(content=self.get_game_text(f"**Tie!** Both were {next_rank}. No risk!"), view=self)
            return

        if self.values[next_rank] < self.values[self.current_rank]:
            self.multiplier += 1
            self.streak += 1

            if self.streak % 5 == 0:
                self.multiplier *= 2
                msg = f"**Streak Bonus!** Multiplicator has been doubled. It was {next_rank}{next_suit}."
            else:
                msg = f"**Correct!** It was {next_rank}{next_suit}."

            self.current_rank, self.current_suit = next_rank, next_suit

            # Cash Out Knopf anschalten
            for child in self.children:
                if child.label == "Cash Out":
                    child.disabled = False

            # WICHTIG: Das view=self MUSS hierhin!
            await interaction.response.edit_message(content=self.get_game_text(msg), view=self)
            
        else: # (Das ist der Verlust)
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(content=f"**{self.ctx.author.display_name} busted!** The card was **{next_rank}{next_suit}**. You lost {self.bet} coins.", view=self)
            self.stop()

    @discord.ui.button(label="Cash Out", style=discord.ButtonStyle.blurple, emoji="💰", disabled=True)
    async def button_cashout(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.ctx.author.id:
            return await interaction.response.send_message("Shoo, it's not your game!", ephemeral=True)

        final_win = int(self.bet * self.multiplier)
        await self.api_client.post(f"http://localhost:5000/economy/update/{self.ctx.author.id}", json={"amount": final_win})

        for child in self.children:
            child.disabled = True
            
        await interaction.response.edit_message(content=f"**Congratulations!** {self.ctx.author.display_name}, you cashed out **{final_win} coins**!", view=self)
        self.stop()

    # BONUS: Damit das Geld nicht verschwindet, wenn der User vergisst zu klicken (Timeout)
    async def on_timeout(self):
        final_win = int(self.bet * self.multiplier)
        try:
            await self.api_client.post(f"http://localhost:5000/economy/update/{self.ctx.author.id}", json={"amount": final_win})
            await self.ctx.send(f"**Timeout!** {self.ctx.author.mention}, you took too long. Your pot of **{final_win} coins** was saved automatically.")
        except:
            pass


class EconomyGames(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.api_client = client.api_client

    def get_card_value(self, card):
        if card in ['J', 'Q', 'K']: return 10
        if card == 'A': return 11
        return int(card)
    
    def calculate_hand(self, hand):
        value = sum(self.get_card_value(c) for c in hand)
        aces = hand.count('A')
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    @commands.command(aliases=['bj'])
    async def blackjack(self, ctx, bet: int):
        if bet <= 0:
            return await ctx.send("You have to place a bet!")
        
        # check balance
        user_id = ctx.author.id
        response = await self.api_client.get(f"http://localhost:5000/balance/{user_id}")
        data = response.json()

        if data.get('balance', 0) < bet:
            return await ctx.send(f"You don't have enough money! Your balance: {data.get('balance')} coins.")
        
        # start game
        deck = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'] * 4
        random.shuffle(deck)

        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        async def get_msg():
            p_val = self.calculate_hand(player_hand)
            return f"**Your hand:** {', '.join(player_hand)} (Value: {p_val})\n**Dealer shows:** {dealer_hand[0]}"
        
        game_msg = await ctx.send(await get_msg() + "\n\nReact with 🃏 to Hit or ✋ to Stand.")
        await game_msg.add_reaction("🃏")
        await game_msg.add_reaction("✋")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["🃏", "✋"] and reaction.message.id == game_msg.id

        try:
            while self.calculate_hand(player_hand) < 21:
                reaction, user = await self.client.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "🃏":
                    player_hand.append(deck.pop())
                    await game_msg.edit(content=await get_msg() + "\n\nReact with 🃏 to Hit or ✋ to Stand.")
                    await game_msg.remove_reaction(reaction, user)
                    if self.calculate_hand(player_hand) >= 21:
                        break
                else:
                    break
        except asyncio.TimeoutError:
            return await ctx.send("Game cancelled (Timeout).")
        
        # result
        player_final = self.calculate_hand(player_hand)

        # check for natural blackjack (2 cards, value 21)
        is_blackjack = len(player_hand) == 2 and player_final == 21

        if player_final > 21:
            result_text = "Bust. You lost!"
            change = -bet
        else:
            # Dealer deals
            while self.calculate_hand(dealer_hand) < 17:
                dealer_hand.append(deck.pop())
            dealer_final = self.calculate_hand(dealer_hand)

            if is_blackjack and not (len(dealer_hand) == 2 and dealer_final == 21):
                win_amount = int(bet * 1.5)
                result_text = f"**BLACKJACK! You won {win_amount}!**"
                change = win_amount
            elif dealer_final > 21 or player_final > dealer_final:
                result_text = f"You won! Dealer had {dealer_final}"
                change = bet
            elif player_final < dealer_final:
                result_text = f"You lost! Dealer had {dealer_final}"
                change = -bet
            else:
                result_text = "Tie!"
                change = 0
        
        # update backend
        # send result to backend
        resp = await self.api_client.post(f"http://localhost:5000/economy/update/{user_id}", json={"amount": change})
        result_data = resp.json()
        new_balance = result_data.get('new_balance', 'unknown')

        await ctx.send(f"**Result:** {result_text}\nYour bet: {bet} | New balance: **{new_balance}** coins.")

    @commands.command(name="top", aliases=["leaderboard"])
    async def top_players(self, ctx):
        response = await self.api_client.get("http://localhost:5000/economy/leaderboard")
        if response.status_code == 200:
            data = response.json()
            
            embed = discord.Embed(
                title="🏆 Top 10 richest users", 
                color=discord.Color.gold(),
                description="rich bois"
            )
            
            for i, entry in enumerate(data, 1):
                user_id = entry['user_id']

                # Versuche den Namen des Users im Discord zu finden
                try:
                    user = await self.client.fetch_user(user_id)
                    user_name = user.display_name 
                except:
                    user_name = f"User not found: {user_id}"
                
                # Medaillen für die ersten drei
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                embed.add_field(
                    name=f"{medal} {user_name}", 
                    value=f"{entry['balance']} Coins", 
                    inline=False)
            
            await ctx.send(embed=embed)
        else:
            await ctx.send("Can't load the leaderboard.")

    @commands.command(name="highlow", aliases=["hl"])
    async def high_low(self, ctx, bet: int):
        if bet <= 0:
            return await ctx.send("Place a bet!")

        response = await self.api_client.get(f"http://localhost:5000/balance/{ctx.author.id}")
        data = response.json()
        if data.get('balance', 0) < bet:
            return await ctx.send("Not enough minerals!")

        # Einsatz sofort abziehen
        await self.api_client.post(f"http://localhost:5000/economy/update/{ctx.author.id}", json={"amount": -bet})

        # Das Tablet einschalten und an die Wand hängen!
        view = HighLowView(ctx, bet, self.api_client)
        await ctx.send(content=view.get_game_text(), view=view)
    
    @commands.command(name="bus")
    async def ride_bus(self, ctx, bet: int):
        if bet <= 0:
            return await ctx.send("Place a bet!")

        response = await self.api_client.get(f"http://localhost:5000/balance/{ctx.author.id}")
        data = response.json()
        if data.get('balance', 0) < bet:
            return await ctx.send("Not enough minerals!")

        # Einsatz sofort abziehen
        await self.api_client.post(f"http://localhost:5000/economy/update/{ctx.author.id}", json={"amount": -bet})

        view = RideTheBusView(ctx, bet, self.api_client)
        await ctx.send(content=view.get_game_text(), view=view)

async def setup(client):
    await client.add_cog(EconomyGames(client))