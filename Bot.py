import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

load_dotenv()


# ==========================================
# 🔒 ALLOWED CATEGORY ID
# ==========================================

ALLOWED_CATEGORY_ID = 1487387217017045134


# ==========================================
# KEEP ALIVE SERVER
# ==========================================

app = Flask("")


@app.route("/")
def home():
    return "Bot is running!"



def run():

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )



def keep_alive():

    t = Thread(target=run)
    t.start()



# ==========================================
# PACK RECOMMENDATIONS
# ==========================================


# ⚡ FASTEST LEVELING
# Prime > Vast > Mediant > Small > Mini

def fastest_leveling(xp):

    packs = {}

    packs["Prime"] = xp // 2_000_000
    xp %= 2_000_000

    packs["Vast"] = xp // 1_100_000
    xp %= 1_100_000

    packs["Mediant"] = xp // 500_000
    xp %= 500_000

    packs["Small"] = xp // 250_000
    xp %= 250_000

    packs["Mini"] = -(-xp // 125_000)

    return packs



# 💰 CHEAPEST COST
# Vast > Mediant > Small > Mini
# NO PRIME

def cheapest_cost(xp):

    packs = {}

    packs["Vast"] = xp // 1_100_000
    xp %= 1_100_000

    packs["Mediant"] = xp // 500_000
    xp %= 500_000

    packs["Small"] = xp // 250_000
    xp %= 250_000

    packs["Mini"] = -(-xp // 125_000)

    return packs



# ==========================================
# DISCORD BOT
# ==========================================

class CalculatorBot(discord.Client):

    def __init__(self):

        super().__init__(
            intents=discord.Intents.all()
        )

        self.tree = app_commands.CommandTree(self)



    async def setup_hook(self):

        await self.tree.sync()



    async def on_ready(self):

        print(
            f"✅ Logged in as {self.user}"
        )



# ==========================================
# CALCULATOR MODAL
# ==========================================

class CalculatorModal(
    discord.ui.Modal,
    title="XP & Pack Calculator"
):


    start_lvl = discord.ui.TextInput(
        label="Start Level",
        placeholder="Example: 1"
    )


    target_lvl = discord.ui.TextInput(
        label="Target Level",
        placeholder="Example: 40"
    )


    current_xp = discord.ui.TextInput(
        label="Current XP",
        required=False,
        placeholder="0"
    )



    async def on_submit(
        self,
        interaction: discord.Interaction
    ):


        try:

            start = int(
                self.start_lvl.value
            )

            target = int(
                self.target_lvl.value
            )

            xp_owned = int(
                self.current_xp.value.strip() or 0
            )


        except ValueError:

            return await interaction.response.send_message(
                "❌ Please use numbers only.",
                ephemeral=True
            )



        # ==================================
        # XP CALCULATION
        # ==================================

        total_xp = 0


        for lvl in range(start, target):

            total_xp += (
                50 * (lvl * lvl + 2)
            )


        total_xp = max(
            0,
            total_xp - xp_owned
        )



        # ==================================
        # PACK RESULTS
        # ==================================

        fast = fastest_leveling(
            total_xp
        )

        cheap = cheapest_cost(
            total_xp
        )



        # ==================================
        # COST
        # ==================================

        prices = {

            "Mini": 15,
            "Small": 20,
            "Mediant": 25,
            "Vast": 45,
            "Prime": 100

        }


        fast_cost = 0

        for name, amount in fast.items():

            fast_cost += (
                prices[name] * amount
            )



        cheap_cost = 0

        for name, amount in cheap.items():

            cheap_cost += (
                prices[name] * amount
            )



        # ==================================
        # TIME
        # ==================================

        times = {

            "Mini": 5,
            "Small": 10,
            "Mediant": 25,
            "Vast": 30,
            "Prime": 30

        }


        total_time = 0


        for name, amount in fast.items():

            total_time += (
                times[name] * amount
            )


        hours = total_time // 60

        minutes = total_time % 60



        # ==================================
        # EMBED
        # ==================================

        emoji = "<:dl:1495834832524021962>"


        embed = discord.Embed(

            title="XP & Pack Calculator",

            color=discord.Color.blurple()

        )


        embed.add_field(

            name="📊 Levels",

            value=f"{start} ➜ {target}",

            inline=False

        )


        embed.add_field(

            name="📈 Total XP Needed",

            value=f"{total_xp:,}",

            inline=False

        )



        icons = {

            "Prime":"👑",
            "Vast":"💎",
            "Mediant":"🌿",
            "Small":"🔥",
            "Mini":"🚀"

        }



        fast_text = ""


        for name, amount in fast.items():

            if amount:

                fast_text += (
                    f"{icons[name]} "
                    f"{amount}x {name} Pack\n"
                )



        embed.add_field(

            name="⚡ Fastest Leveling",

            value=fast_text or "None",

            inline=False

        )



        cheap_text = ""


        for name, amount in cheap.items():

            if amount:

                cheap_text += (
                    f"{icons[name]} "
                    f"{amount}x {name} Pack\n"
                )



        embed.add_field(

            name="💰 Cheapest Cost",

            value=cheap_text or "None",

            inline=False

        )



        embed.add_field(

            name="💸 Fastest Cost",

            value=f"{fast_cost}{emoji} DL",

            inline=False

        )


        embed.add_field(

            name="💰 Cheapest Cost",

            value=f"{cheap_cost}{emoji} DL",

            inline=False

        )


        embed.add_field(

            name="⏱️ Estimated Time",

            value=f"{hours}h {minutes}m",

            inline=False

        )



        await interaction.response.send_message(
            embed=embed
        )



# ==========================================
# COMMAND
# ==========================================

bot = CalculatorBot()



@bot.tree.command(
    name="calc",
    description="Open XP Calculator"
)

async def calc(
    interaction: discord.Interaction
):


    if (

        interaction.channel is None

        or interaction.channel.category is None

        or interaction.channel.category.id != ALLOWED_CATEGORY_ID

    ):

        return await interaction.response.send_message(

            "❌ This command can only be used in the allowed category.",

            ephemeral=True

        )



    await interaction.response.send_modal(
        CalculatorModal()
    )



# ==========================================
# RUN
# ==========================================

if __name__ == "__main__":

    keep_alive()

    token = os.getenv(
        "DISCORD_TOKEN"
    )

    bot.run(token)
