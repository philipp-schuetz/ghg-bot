import os
import sqlite3
import time
from datetime import datetime

import discord
from discord import app_commands

TOKEN_DISCORD = os.getenv("TOKEN_DISCORD")
ID_GUILD = discord.Object(id=os.getenv("TOKEN_GUILD"))


con = sqlite3.connect("bot-database.db")
cur = con.cursor()


def get_events(cur):
    result = cur.execute("SELECT title, description, timestamp FROM events")
    res_list = result.fetchall()

    res_str = ""
    i = 0
    for event in res_list:
        for column in event:
            if isinstance(column, int):
                column = datetime.fromtimestamp(column).strftime("%d/%m/%Y")
            if i == 0 or i == 2:
                column = "**" + column + "**"
            res_str += column
            res_str += " "
            i += 1
        res_str += "\n"
        i = 0

    if res_str != "":
        return res_str
    else:
        return None


def add_event(title: str, description: str, date: str, con, cur):
    timestamp = time.mktime(datetime.strptime(date, "%d/%m/%Y").timetuple())
    cur.execute("INSERT INTO events (title, description, timestamp) VALUES (?, ?, ?)", (title, description, timestamp))
    con.commit()


def del_event(title, con, cur):
    cur.execute("DELETE FROM events WHERE title=?", (title,))
    con.commit()


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=ID_GUILD)
        await self.tree.sync(guild=ID_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command()
async def help(interaction: discord.Interaction):
    """Zeigt Hilfe an"""
    response = """
    /website:
    \u2022 home: Homepage
    \u2022 fehlzeiten: Fehlzeiten Formular

    /events: Zeigt Events an
    /addevent: Erstellt Event
    /delevent: Löscht Event
    """

    embed = discord.Embed(title="Help", description=response, colour=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command()
@app_commands.rename(site="seite")
@app_commands.choices(site=[
    app_commands.Choice(name="home", value="https://www.herwegh-gymnasium.de"),
    app_commands.Choice(name="fehlzeiten", value="https://www.herwegh-gymnasium.de/organisation/formulare/schueler/Entschuldigungszettel.pdf")
])
async def website(interaction: discord.Interaction, site: app_commands.Choice[str]):
    """Generiert Website Link"""
    await interaction.response.send_message(site.value, ephemeral=True)


@client.tree.command()
async def events(interaction: discord.Interaction):
    """Zeigt zukünftige Events an"""
    res = get_events(cur)
    if res == None:
        res = "Keine Events verfügbar."
    embed = discord.Embed(title="Events", description=res, colour=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command()
@app_commands.rename(title="titel", description="beschribung", date="datum")
@app_commands.describe(date="(01/01/2000)")
async def addevent(interaction: discord.Interaction, title: str, description: str, date: str):
    """Erstellt Event"""
    add_event(title, description, date, con, cur)
    await interaction.response.send_message(f"Event '{title}' erstellt.")


@client.tree.command()
@app_commands.rename(title="titel")
async def delevent(interaction: discord.Interaction, title: str):
    """Löscht Event"""
    del_event(title, con, cur)
    await interaction.response.send_message(f"Event '{title}' gelöscht.")


client.run(TOKEN_DISCORD)
