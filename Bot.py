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
# KEEP ALIVE SERVER (RENDER)
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

    Thread(
        target=run
    ).start()



# ==========================================
# PACK FUNCTIONS
# ==========================================


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
# PACK DATA
# ==========================================


PRICES = {

    "Mini":15,
    "Small":20,
    "Mediant":25,
    "Vast":45,
    "Prime":100

}


TIMES = {

    "Mini":5,
    "Small":10,
    "Mediant":25,
    "Vast":30,
    "Prime":30

}


ICONS = {

    "Prime":"👑",
    "Vast":"💎",
    "Mediant":"🌿",
    "Small":"🔥",
    "Mini":"🚀"

}

# ==========================================
# PAGINATION VIEW
# ==========================================


class CalculatorView(discord.ui.View):

    def __init__(
        self,
        fast_text,
        cheap_text,
        total_xp,
        start,
        target,
        fast_cost,
        cheap_cost,
        hours,
        minutes,
        cheap_hours,
        cheap_minutes
    ):

        super().__init__(
            timeout=None
        )

        self.fast_text = fast_text
        self.cheap_text = cheap_text

        self.total_xp = total_xp

        self.start = start
        self.target = target

        self.fast_cost = fast_cost
        self.cheap_cost = cheap_cost

        self.hours = hours
        self.minutes = minutes

        self.cheap_hours = cheap_hours
        self.cheap_minutes = cheap_minutes



    # ======================================
    # PAGE 2
    # ======================================

    @discord.ui.button(
        label="➡️ Next",
        style=discord.ButtonStyle.primary,
        custom_id="xp_calc_next"
    )
    async def next_page(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        emoji = "<:dl:1495834832524021962>"


        embed = discord.Embed(

            title="XP & Pack Calculator",

            color=discord.Color.gold()

        )


        embed.add_field(

            name="📊 Levels",

            value=f"{self.start} ➜ {self.target}",

            inline=False

        )


        embed.add_field(

            name="📈 Total XP Needed",

            value=f"{self.total_xp:,}",

            inline=False

        )


        embed.add_field(

            name="💰 Cheapest Pack",

            value=self.cheap_text or "None",

            inline=False

        )


        embed.add_field(

            name="💸 Cheapest Cost",

            value=f"{self.cheap_cost} {emoji} DL",

            inline=False

        )


        embed.add_field(

            name="⏱️ Estimated Time",

            value=f"{self.cheap_hours}h {self.cheap_minutes}m",

            inline=False

        )


        embed.set_footer(

            text="Page 2/2"

        )


        await interaction.response.edit_message(

            embed=embed,

            view=self

        )




    # ======================================
    # PAGE 1
    # ======================================


    @discord.ui.button(

        label="⬅️ Back",

        style=discord.ButtonStyle.secondary,

        custom_id="xp_calc_back"

    )
    async def back_page(

        self,

        interaction: discord.Interaction,

        button: discord.ui.Button

    ):


        emoji = "<:dl:1495834832524021962>"


        embed = discord.Embed(

            title="XP & Pack Calculator",

            color=discord.Color.blurple()

        )


        embed.add_field(

            name="📊 Levels",

            value=f"{self.start} ➜ {self.target}",

            inline=False

        )


        embed.add_field(

            name="📈 Total XP Needed",

            value=f"{self.total_xp:,}",

            inline=False

        )


        embed.add_field(

            name="⚡ Fastest Leveling",

            value=self.fast_text or "None",

            inline=False

        )


        embed.add_field(

            name="💸 Fastest Cost",

            value=f"{self.fast_cost} {emoji} DL",

            inline=False

        )


        embed.add_field(

            name="⏱️ Estimated Time",

            value=f"{self.hours}h {self.minutes}m",

            inline=False

        )


        embed.set_footer(

            text="Page 1/2"

        )


        await interaction.response.edit_message(

            embed=embed,

            view=self

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
                self.current_xp.value or 0
            )


        except ValueError:


            return await interaction.response.send_message(

                "❌ Please enter numbers only.",

                ephemeral=True

            )



        if target <= start:


            return await interaction.response.send_message(

                "❌ Target level must be higher than start level.",

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



        fast = fastest_leveling(

            total_xp

        )


        cheap = cheapest_cost(

            total_xp

        )



        fast_text = ""


        for name, amount in fast.items():

            if amount:

                fast_text += (

                    f"{ICONS[name]} {amount}x {name} Pack\n"

                )



        cheap_text = ""


        for name, amount in cheap.items():

            if amount:

                cheap_text += (

                    f"{ICONS[name]} {amount}x {name} Pack\n"

                )



        # ==================================
        # COST
        # ==================================


        fast_cost = sum(

            PRICES[name] * amount

            for name, amount in fast.items()

        )


        cheap_cost = sum(

            PRICES[name] * amount

            for name, amount in cheap.items()

        )



        # ==================================
        # TIME
        # ==================================


        fast_time = sum(

            TIMES[name] * amount

            for name, amount in fast.items()

        )


        cheap_time = sum(

            TIMES[name] * amount

            for name, amount in cheap.items()

        )



        hours = fast_time // 60

        minutes = fast_time % 60


        cheap_hours = cheap_time // 60

        cheap_minutes = cheap_time % 60



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


        embed.add_field(

            name="⚡ Fastest Leveling",

            value=fast_text or "None",

            inline=False

        )


        embed.add_field(

            name="💸 Fastest Cost",

            value=f"{fast_cost} {emoji} DL",

            inline=False

        )


        embed.add_field(

            name="⏱️ Estimated Time",

            value=f"{hours}h {minutes}m",

            inline=False

        )


        embed.set_footer(

            text="Page 1/2"

        )



        view = CalculatorView(

            fast_text,

            cheap_text,

            total_xp,

            start,

            target,

            fast_cost,

            cheap_cost,

            hours,

            minutes,

            cheap_hours,

            cheap_minutes

        )



        await interaction.response.send_message(

            embed=embed,

            view=view

        )





# ==========================================
# BOT SETUP
# ==========================================


class CalculatorBot(discord.Client):


    def __init__(self):

        super().__init__(

            intents=discord.Intents.all()

        )

        self.tree = app_commands.CommandTree(self)



    async def setup_hook(self):


        self.add_view(

            CalculatorView(

                "",
                "",
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0

            )

        )


        await self.tree.sync()



    async def on_ready(self):

        print(

            f"✅ Logged in as {self.user}"

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
