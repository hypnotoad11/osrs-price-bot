import discord
from discord.ext import commands
import asyncio
import aiohttp
from datetime import datetime, timedelta

# >>> REPLACE THESE TWO WITH YOUR REAL VALUES <<<
TOKEN = "MTQ1OTgyMDU2Mzk1NzY4MjIyNw.GxJv-k.X08seJZjh3Ai8rSWlYVTig3tpkRDq-10-XZEo0"
CHANNEL_ID = 1459818494358061136
  # replace with your channel ID, just the numbers
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Store timestamps + prices for last hour
price_history = []

async def fetch_price(item_id):
    url = f"https://prices.runescape.wiki/api/v1/osrs/latest?id={item_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            return data["data"][str(item_id)]["high"]


# -----------------------------
# PRICE COMMANDS
# -----------------------------

@bot.command()
async def dpick(ctx):
    """Check the current Dragon pickaxe price."""
    price = await fetch_price(11920)
    await ctx.send(f"🪓 **Dragon Pickaxe Price:** {price:,} gp")


@bot.command()
async def price(ctx, item_id: int):
    """Check the price of any OSRS item by ID."""
    try:
        price = await fetch_price(item_id)
        await ctx.send(f"📦 **Item {item_id} Price:** {price:,} gp")
    except:
        await ctx.send("Couldn't fetch that item. Check the ID and try again.")


# -----------------------------
# 150% SPIKE CHECK LOOP
# -----------------------------

async def price_check_loop():
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    while True:
        try:
            current_price = await fetch_price(11920)
            now = datetime.utcnow()

            # Add new price to history
            price_history.append((now, current_price))

            # Remove entries older than 1 hour
            one_hour_ago = now - timedelta(hours=1)
            while price_history and price_history[0][0] < one_hour_ago:
                price_history.pop(0)

            # Check for 150% spike
            if len(price_history) > 1:
                old_price = price_history[0][1]

                if old_price > 0:
                    increase = (current_price - old_price) / old_price

                    if increase >= 1.5:
                        await channel.send(
                            f"🚨 **Dragon Pickaxe Spike Detected!**\n"
                            f"Price increased **150%+** in the last hour.\n"
                            f"Old price: {old_price:,} gp\n"
                            f"Current price: {current_price:,} gp"
                        )

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(15 * 60)  # 15 minutes


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(price_check_loop())


bot.run(TOKEN)
