# bots/discord_bot.py — CLÆRK Discord Bot

import os
import logging
import random
import core  # Persuasion engine
import requests
from datetime import datetime

import discord
from discord.ext import commands, tasks

logger = logging.getLogger("claerk.discordbot")
logging.basicConfig(level=logging.INFO)

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.environ.get("DISCORD_CHANNEL_ID", 0))
COMMAND_PREFIX = "!"
ADMIN_ROLE = os.environ.get("DISCORD_ADMIN_ROLE", "Admin")

bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=discord.Intents.all())

# --- Utility: Generate message using LLM + persuasion ---
def generate_discord_message(product, persona="beginner", use_llm=True, context=None):
    context = context or {}
    base = f"Check out **{product['title']}** — {product['description']}"
    context.update({
        "persona": persona,
        "platform": "discord",
        "main_benefit": product.get("category"),
        "product_type": product.get("product_type"),
        "locale": product.get("locale", "en"),
    })
    msg = base
    if use_llm:
        try:
            resp = requests.post(
                os.environ.get("LLM_GATEWAY_URL", "http://localhost:9999/llm/generate"),
                json={
                    "prompt": f"Write a friendly, high-conversion Discord post about {product['title']} ({product['description']}). Persona: {persona}.",
                    "provider": "ollama", "model": "llama3", "max_tokens": 120
                },
                timeout=15
            )
            msg = resp.json().get("response", base)
        except Exception as e:
            logger.warning(f"LLM error for Discord: {e}")
    return core.apply_principles(msg, context)

# --- Events ---

@bot.event
async def on_ready():
    logger.info(f"Discord Bot connected as {bot.user}")
    if DISCORD_CHANNEL_ID:
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            await channel.send("CLÆRK Discord Bot is now online! Use !product or !offer for a new deal.")
    campaign_poster.start()

# --- Campaign Poster Task (scheduled interval) ---
@tasks.loop(minutes=30)
async def campaign_poster():
    if not DISCORD_CHANNEL_ID:
        logger.warning("No DISCORD_CHANNEL_ID set, skipping scheduled post.")
        return
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if not channel:
        logger.warning("Discord channel not found.")
        return
    # Example: Load products from JSON dir (or DB)
    from pathlib import Path
    import json
    files = list(Path("products").glob("*.json"))
    if not files:
        return
    product = json.load(open(random.choice(files)))
    msg = generate_discord_message(product)
    await channel.send(msg)

# --- Command: !product (send a random product) ---
@bot.command()
async def product(ctx):
    from pathlib import Path
    import json
    files = list(Path("products").glob("*.json"))
    if not files:
        await ctx.send("No products available.")
        return
    product = json.load(open(random.choice(files)))
    msg = generate_discord_message(product)
    await ctx.send(msg)

# --- Command: !offer (send random offer/affiliate link) ---
@bot.command()
async def offer(ctx):
    from pathlib import Path
    import json
    files = list(Path("products").glob("*.json"))
    if not files:
        await ctx.send("No offers at this time.")
        return
    product = json.load(open(random.choice(files)))
    offer_link = os.environ.get("AFFILIATE_LINKS", "https://your-link.com").split(",")[0]
    msg = f"{generate_discord_message(product)}\nSpecial link: {offer_link}"
    await ctx.send(msg)

# --- Moderation Command Example: !mute, !ban ---
@bot.command()
@commands.has_role(ADMIN_ROLE)
async def mute(ctx, member: discord.Member, *, reason=None):
    await member.edit(mute=True)
    await ctx.send(f"Muted {member.display_name}.")

@bot.command()
@commands.has_role(ADMIN_ROLE)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"Banned {member.display_name}.")

# --- Error Logging ---
@bot.event
async def on_command_error(ctx, error):
    logger.error(f"Discord command error: {error}")
    await ctx.send(f"Error: {error}")

# --- DMs: Respond to "generate for me" ---
@bot.event
async def on_message(message):
    if message.guild is None and message.content.lower().startswith("generate"):
        persona = "beginner"
        from pathlib import Path
        import json
        files = list(Path("products").glob("*.json"))
        if files:
            product = json.load(open(random.choice(files)))
            msg = generate_discord_message(product, persona=persona)
            await message.author.send(msg)
        else:
            await message.author.send("Sorry, no products available right now.")
    await bot.process_commands(message)

# --- Run Bot ---
if __name__ == "__main__":
    if DISCORD_BOT_TOKEN:
        bot.run(DISCORD_BOT_TOKEN)
    else:
        logger.error("DISCORD_BOT_TOKEN not set.")
