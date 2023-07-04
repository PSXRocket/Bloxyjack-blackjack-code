import discord
from discord.app_commands import choices
import json
import random
import time
import datetime
import requests
import string
from enum import Enum
import cloudscraper
import asyncio 
from discord import app_commands
from discord.ext import commands
import os, threading, multiprocessing

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)
    print("packski2 is daddy and also bot is ready to listen to commands.")


def get_random_card():
    suits = ['♠️', '♣️', '♥️', '♦️']
    ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    return random.choice(ranks) + random.choice(suits)

def calculate_hand_score(hand):
    score = 0
    ace_count = 0

    for card in hand:
        if card[0] == 'A':
            score += 11
            ace_count += 1
        elif card[0] in ['K', 'Q', 'J']:
            score += 10
        elif card[:2] == '10':
            score += 10
        elif card[0].isdigit():
            score += int(card[0])

    # Adjust for aces
    while score > 21 and ace_count > 0:
        score -= 10
        ace_count -= 1

    return score

class Blackjack(discord.ui.View):
    def __init__(self, authorid, gems, playerusername, playercard1, playercard2, dealercard1, dealercard2, playerhand, dealerhand, playercardvalue, dealercardvalue):
        super().__init__(timeout=None)
        self.author_id = authorid
        self.gems = gems
        self.playerusername = playerusername
        self.playercard1 = playercard1
        self.playercard2 = playercard2
        self.dealercard1 = dealercard1
        self.dealercard2 = dealercard2
        self.playerhand = playerhand
        self.dealerhand = dealerhand
        self.playercardvalue = playercardvalue
        self.dealercardvalue = dealercardvalue
        self.playerhandb = NotImplemented
        self.dealerhandb = NotImplemented
    
    @discord.ui.button(label=f"Hit", style=discord.ButtonStyle.green, custom_id="hit")
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            embed = discord.Embed(title="❌ Blackjack Error", color=0x47a8e8)
            embed.description = "You aren't the author of this game."
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        newCard = get_random_card()
        self.playerhand.append(newCard)
        self.playercardvalue = calculate_hand_score(self.playerhand)
        self.playerhandb = ' '.join(self.playerhand)
        self.dealerhandb = ''.join(self.dealerhand)

        if self.playercardvalue >= 22:
            embed = discord.Embed(title="🃏 Blackjack - You **LOST**", color=discord.Colour.red())
            embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
            embed.description = f":gem: Bet: {shorten_number(self.gems)}"
            embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
            embed.add_field(name="Dealer's Hand", value=f"`{self.dealerhandb}`\nDealer's Card Value: `{self.dealercardvalue}`", inline=False)
            embed.set_footer(text="You have lost this round.")

            for child in self.children:
                child.disabled = True

            await interaction.response.edit_message(embed = embed, view=self)
        elif self.playercardvalue <= 20:
            embed = discord.Embed(title="🃏 Blackjack", color=0x47a8e8)
            embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
            embed.description = f":gem: Bet: {shorten_number(self.gems)}\n🎊 Potential Winnings: {shorten_number(self.gems * 2)}"
            embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
            embed.add_field(name="Dealer's Hand", value=f"`{self.dealercard1}` ??\nDealer's Card Value: `??`", inline=False)
            embed.set_footer(text="Good luck!")

            await interaction.response.edit_message(embed = embed)
        elif self.playercardvalue == 21:
            embed = discord.Embed(title="🃏 Blackjack", color=0x47a8e8)
            embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
            embed.description = f":gem: Bet: {shorten_number(self.gems)}\n🎊 Winnings: {shorten_number(self.gems * 2)}"
            embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
            embed.add_field(name="Dealer's Hand", value=f"`{self.dealercard1}` ??\nDealer's Card Value: `??`", inline=False)
            embed.set_footer(text="You have gained 21!")

            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(embed = embed, view=self)

            while self.dealercardvalue < 17:
                newcard = get_random_card()
                self.dealerhand.append(newcard)
                self.dealercardvalue = calculate_hand_score(self.dealerhand)
                embed = discord.Embed(title="🃏 Blackjack", color=0x47a8e8)
                embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
                embed.description = f":gem: Bet: {shorten_number(self.gems)}\n🎊 Potential Winnings: {shorten_number(self.gems * 2)}"
                embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
                embed.add_field(name="Dealer's Hand", value=f"`{self.dealerhandb}`\nDealer's Card Value: `{self.dealercardvalue}`", inline=False)
                embed.set_footer(text="Good luck!")
                await interaction.edit_original_response(embed = embed, view=self)
                await asyncio.sleep(1)
        
            if self.dealercardvalue >= 17 and self.dealercardvalue > self.playercardvalue:
                embed = discord.Embed(title="🃏 Blackjack - You **LOST**", color=discord.Colour.red())
                embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
                embed.description = f":gem: Bet: {shorten_number(self.gems)}"
                embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
                embed.add_field(name="Dealer's Hand", value=f"`{self.dealerhandb}`\nDealer's Card Value: `{self.dealercardvalue}`", inline=False)
                embed.set_footer(text="You have lost this round.")

                await interaction.edit_original_response(embed = embed)
            
            if self.dealercardvalue >= 17 and self.dealercardvalue == self.playercardvalue:
                embed = discord.Embed(title="🃏 Blackjack - You Pushed!", color=0x47a8e8)
                embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
                embed.description = f":gem: Bet: {shorten_number(self.gems)}\n🎊 Push: {shorten_number(self.gems)}"
                embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
                embed.add_field(name="Dealer's Hand", value=f"`{self.dealerhandb}`\nDealer's Card Value: `{self.dealercardvalue}`", inline=False)
                embed.set_footer(text="You pushed!")

                winnings = self.gems
                await update_wallet(interaction.user, winnings)
                await interaction.edit_original_response(embed=embed)

            if self.dealercardvalue >= 17 and self.dealercardvalue < self.playercardvalue:
                embed = discord.Embed(title="🃏 Blackjack - You Won!", color=discord.Color.green())
                embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
                embed.description = f":gem: Bet: {shorten_number(self.gems)}\n🎊 Push: {shorten_number(self.gems * 2)}"
                embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
                embed.add_field(name="Dealer's Hand", value=f"`{self.dealerhandb}`\nDealer's Card Value: `{self.dealercardvalue}`", inline=False)
                embed.set_footer(text="You won!")

                winnings = self.gems * 2
                await update_wallet(interaction.user, winnings)
                await interaction.edit_original_response(embed=embed)
            
            if self.dealercardvalue >= 22 and self.playercardvalue <= 21:
                embed = discord.Embed(title="🃏 Blackjack - You Won!", color=discord.Color.green())
                embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
                embed.description = f":gem: Bet: {shorten_number(self.gems)}\n🎊 Push: {shorten_number(self.gems * 2)}"
                embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
                embed.add_field(name="Dealer's Hand", value=f"`{self.dealerhandb}`\nDealer's Card Value: `{self.dealercardvalue}`", inline=False)
                embed.set_footer(text="You won!")

                winnings = self.gems * 2
                await update_wallet(interaction.user, winnings)
                await interaction.edit_original_response(embed=embed)


    @discord.ui.button(label=f"Stand", style=discord.ButtonStyle.red, custom_id="stand")
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            embed = discord.Embed(title="❌ Blackjack Error", color=0x47a8e8)
            embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
            embed.description = "You aren't the author of this game."
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        for child in self.children:
            child.disabled = True

        self.playerhandb = ' '.join(self.playerhand)
        self.dealerhandb = ''.join(self.dealerhand)
        embed = discord.Embed(title="🃏 Blackjack", color=0x47a8e8)
        embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
        embed.description = f":gem: Bet: {shorten_number(self.gems)}\n🎊 Potential Winnings: {shorten_number(self.gems * 2)}"
        embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
        embed.add_field(name="Dealer's Hand", value=f"`{self.dealerhandb}`\nDealer's Card Value: `{self.dealercardvalue}`", inline=False)
        embed.set_footer(text="Good luck!")

        await interaction.response.edit_message(embed = embed, view=self)

        await asyncio.sleep(2)
        
        while self.dealercardvalue < 17:
            newcard = get_random_card()
            self.dealerhand.append(newcard)
            self.dealercardvalue = calculate_hand_score(self.dealerhand)
            self.dealerhandb = ''.join(self.dealerhand)
            embed = discord.Embed(title="🃏 Blackjack", color=0x47a8e8)
            embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
            embed.description = f":gem: Bet: {shorten_number(self.gems)}\n🎊 Potential Winnings: {shorten_number(self.gems * 2)}"
            embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
            embed.add_field(name="Dealer's Hand", value=f"`{self.dealerhandb}`\nDealer's Card Value: `{self.dealercardvalue}`", inline=False)
            embed.set_footer(text="Good luck!")
            await interaction.edit_original_response(embed = embed, view=self)
            await asyncio.sleep(1)

        await asyncio.sleep(1)
        
        if self.dealercardvalue >= 17 and self.dealercardvalue > self.playercardvalue and self.dealercardvalue <= 21:
            embed = discord.Embed(title="🃏 Blackjack - You **LOST**", color=discord.Colour.red())
            embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
            embed.description = f":gem: Bet: {shorten_number(self.gems)}"
            embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
            embed.add_field(name="Dealer's Hand", value=f"`{self.dealerhandb}`\nDealer's Card Value: `{self.dealercardvalue}`", inline=False)
            embed.set_footer(text="You have lost this round.")

            await interaction.edit_original_response(embed = embed)
        
        if self.dealercardvalue >= 17 and self.dealercardvalue == self.playercardvalue and self.dealercardvalue <= 21:
            embed = discord.Embed(title="🃏 Blackjack - You Pushed!", color=0x47a8e8)
            embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
            embed.description = f":gem: Bet: {shorten_number(self.gems)}\n🎊 Push: {shorten_number(self.gems)}"
            embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
            embed.add_field(name="Dealer's Hand", value=f"`{self.dealerhandb}`\nDealer's Card Value: `{self.dealercardvalue}`", inline=False)
            embed.set_footer(text="You pushed!")

            winnings = self.gems
            await update_wallet(interaction.user, winnings)
            await interaction.edit_original_response(embed=embed)

        if self.dealercardvalue >= 17 and self.dealercardvalue < self.playercardvalue and self.playercardvalue <= 21:
            embed = discord.Embed(title="🃏 Blackjack - You Won!", color=discord.Color.green())
            embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
            embed.description = f":gem: Bet: {shorten_number(self.gems)}\n🎊 Winnings: {shorten_number(self.gems * 2)}"
            embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
            embed.add_field(name="Dealer's Hand", value=f"`{self.dealerhandb}`\nDealer's Card Value: `{self.dealercardvalue}`", inline=False)
            embed.set_footer(text="You won!")

            winnings = self.gems * 2
            await update_wallet(interaction.user, winnings)
            await interaction.edit_original_response(embed=embed)
        
        if self.dealercardvalue > 21 and self.playercardvalue <= 21:
            embed = discord.Embed(title="🃏 Blackjack - You Won!", color=discord.Color.green())
            embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
            embed.description = f":gem: Bet: {shorten_number(self.gems)}\n🎊 Winnings: {shorten_number(self.gems * 2)}"
            embed.add_field(name=f"{self.playerusername}'s Hand", value=f"`{self.playerhandb}`\nPlayer's Card Value: `{self.playercardvalue}`", inline=False)
            embed.add_field(name="Dealer's Hand", value=f"`{self.dealerhandb}`\nDealer's Card Value: `{self.dealercardvalue}`", inline=False)
            embed.set_footer(text="You won!")

            winnings = self.gems * 2
            await update_wallet(interaction.user, winnings)
            await interaction.edit_original_response(embed=embed)

# blackjack
@bot.tree.command(name="blackjack", description="Play a game of blackjack")
@commands.guild_only()
@commands.cooldown(1, 5)
async def blackjack(interaction: discord.Interaction, gems: str):
    try:
        gems = parse_amount(gems)
    except ValueError:
        embed = discord.Embed(title="❌ Blackjack Creation Failed", color=0x47a8e8)
        embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
        embed.description = "Enter a valid amount of gems to continue with this transaction."
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    if gems < 100_000_000:
        embed = discord.Embed(title="❌ Blackjack Creation Failed", color=0x47a8e8)
        embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
        embed.description = "Amount must be greater than **100M gems.**"
        return await interaction.response.send_message(embed=embed)
    
    if gems < 100_000_000:
        embed = discord.Embed(title="❌ Blackjack Creation Failed", color=0x47a8e8)
        embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
        embed.description = "Amount must be greater than **100M gems.**"
        return await interaction.response.send_message(embed=embed)

    balance = await get_balance(interaction.user)
    if balance < gems:
        embed = discord.Embed(title="❌ Blackjack Creation Failed", color=0x47a8e8)
        embed.description = "You don't have enough gems to complete this transaction."
        return await interaction.response.send_message(embed=embed)
    
    await update_wallet(interaction.user, -gems)
    await update_wagered_amount(interaction.user.id, gems)

    player_username = interaction.user.name
    player_card1 = get_random_card()
    player_card2 = get_random_card()
    dealer_card1 = get_random_card()
    dealer_card2 = get_random_card()
    
    player_hand = [player_card1, player_card2]
    player_handb = ' '.join(player_hand)
    dealer_hand = [dealer_card1, dealer_card2]
    dealer_handb = ' '.join(dealer_hand)
    player_card_value = calculate_hand_score(player_hand)
    dealer_card_value = calculate_hand_score(dealer_hand) 

    justStarted = True

    if justStarted == True:
        if player_card_value == 21:
            if player_card_value == dealer_card_value:
                embed = discord.Embed(title="🃏 Blackjack - You Pushed!", color=discord.Color.orange())
                embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
                embed.description = f":gem: Bet: {shorten_number(gems)}\n🎊 Push: {shorten_number(gems)}"
                embed.add_field(name=f"{player_username}'s Hand", value=f"`{player_handb}`\nPlayer's Card Value: `{player_card_value}`", inline=False)
                embed.add_field(name="Dealer's Hand", value=f"`{dealer_handb}`\nDealer's Card Value: `{dealer_card_value}`", inline=False)
                embed.set_footer(text="You pushed!")
                justStarted = False
                winnings = gems
                await update_wallet(interaction.user, winnings)
                await interaction.response.send_message(embed=embed)
            elif justStarted == True and player_card_value == 21 and dealer_card_value <= 20:
                embed = discord.Embed(title="🃏 Blackjack - You Win!", color=discord.Color.green())
                embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
                embed.description = f":gem: Bet: {shorten_number(gems)}\n🎊 Potential Winnings: {shorten_number(gems * 2)}"
                embed.add_field(name=f"{player_username}'s Hand", value=f"`{player_handb}`\nPlayer's Card Value: `{player_card_value}`", inline=False)
                embed.add_field(name="Dealer's Hand", value=f"`{dealer_handb}`\nDealer's Card Value: `{dealer_card_value}`", inline=False)
                embed.set_footer(text="You win 2.5x your bet amount!")

                winnings = gems*2.5
                await update_wallet(interaction.user, winnings)

                justStarted = False
                await interaction.response.send_message(embed=embed)
        elif dealer_card_value == 21:
            embed = discord.Embed(title="🃏 Blackjack - You Lost!", color=discord.Color.red())
            embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
            embed.description = f":gem: Bet: {shorten_number(gems)}"
            embed.add_field(name=f"{player_username}'s Hand", value=f"`{player_handb}`\nPlayer's Card Value: `{player_card_value}`", inline=False)
            embed.add_field(name="Dealer's Hand", value=f"`{dealer_handb}`\nDealer's Card Value: `{dealer_card_value}`", inline=False)
            embed.set_footer(text="You Lost!")

            justStarted = False
            await interaction.response.send_message(embed=embed)
        else:
            v = Blackjack(interaction.user.id, gems, player_username, player_card1, player_card2, dealer_card1, dealer_card2, player_hand, dealer_hand, player_card_value, dealer_card_value)
            
            embed = discord.Embed(title="🃏 Blackjack", color=0x47a8e8)
            embed.set_author(name='Bloxyjack', icon_url='https://media.discordapp.net/attachments/1120434860121673801/1121242599987101716/BloxyJack.png')
            embed.description = f":gem: Bet: {shorten_number(gems)}\n🎊 Potential Winnings: {shorten_number(gems * 2)}"
            embed.add_field(name=f"{player_username}'s Hand", value=f"`{player_handb}`\nPlayer's Card Value: `{player_card_value}`", inline=False)
            embed.add_field(name="Dealer's Hand", value=f"`{dealer_card1}` ??\nDealer's Card Value: `??`", inline=False)
            embed.set_footer(text="Good luck!")
            
            justStarted = False
            await interaction.response.send_message(embed=embed, view=v)
bot.run("ur token")
