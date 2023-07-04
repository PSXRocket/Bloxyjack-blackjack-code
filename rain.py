participants = {}
rain_msg = None  # Declare rain_msg variable outside the functions

def check(reaction, user):
    return str(reaction.emoji) == '🌧' and reaction.message.id == rain_msg.id and not user.bot

@bot.tree.command(name="rain", description="start a Rain Event")
async def rain(interaction: discord.Interaction, amount_str: str):

    balance = await get_balance(interaction.user)

    gems = parse_amount(amount_str)

    if gems < 100_000_000:
        await interaction.response.send_message("The amount to be rained must be at least :diamond:: 100M.")
        return
    if gems > balance:
        await interaction.response.send_message(f"You don't have enough :diamond: to start a rain.")
        return
    rain_channel = bot.get_channel(1114585394760122510)
    if not rain_channel:
        await interaction.response.send_message("Could not find the rain channel")
        return
    await update_wallet(interaction.user, -gems)

    embed = discord.Embed(title=":rain: Rain Incoming", color=0x00bfff)
    embed.set_author(name=f"Hosted by {interaction.user.display_name}")
    embed.add_field(name=":diamond: | Amount", value=f"{shorten_number(gems)}")
    embed.set_footer(text="React with 🌧 to join")
    global rain_msg  # Update rain_msg variable
    rain_msg = await rain_channel.send(embed=embed)
    await interaction.response.send_message("Success", ephemeral=True)
    await rain_msg.add_reaction("🌧")

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            participants[user.id] = True
        except asyncio.TimeoutError:
            break

    if not participants:
        await rain_channel.send("No one joined the rain event :(")
        return

    share_amount = amount // len(participants)

    await update_wallet(participants, +share_amount)

    formatted_winnings = format_number(share_amount)
    embed = discord.Embed(title="☁️ Rain Ended", description="All users who joined the rain have been awarded the pot")
    await rain_channel.send(embed=embed)
