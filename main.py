import os
import sqlite3
import time
from datetime import datetime

import discord
from discord import app_commands

TOKEN_DISCORD = os.getenv("TOKEN_DISCORD")
ID_GUILD = discord.Object(id=os.getenv("ID_GUILD"))


db_connection = sqlite3.connect("/db/bot-database.db")
db_cursor = db_connection.cursor()


def get_events(cursor: sqlite3.Cursor) -> str:
    result = cursor.execute("SELECT title, description, timestamp FROM events")
    res_list = result.fetchall()

    events = []
    for event in res_list:
        events.append(f"**{event[0]}** {event[1]} **<t:{event[2]}:D>**")

    return "\n".join(events) if len(events) > 0 else "keine Events verfügbar"


def add_event(title: str, description: str, date: str, connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    timestamp = time.mktime(datetime.strptime(date, "%d/%m/%Y").timetuple())
    cursor.execute("INSERT INTO events (title, description, timestamp) VALUES (?, ?, ?)", (title, description, timestamp))
    connection.commit()


def del_event(title, connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    cursor.execute("DELETE FROM events WHERE title=?", (title,))
    connection.commit()



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
    result = get_events(db_cursor)
    embed = discord.Embed(title="Events", description=result, colour=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command()
@app_commands.rename(title="titel", description="beschribung", date="datum")
@app_commands.describe(date="(01/01/2000)")
async def addevent(interaction: discord.Interaction, title: str, description: str, date: str):
    """Erstellt Event"""
    add_event(title, description, date, db_connection, db_cursor)
    await interaction.response.send_message(f"Event '{title}' erstellt.")


@client.tree.command()
@app_commands.rename(title="titel")
async def delevent(interaction: discord.Interaction, title: str):
    """Löscht Event"""
    del_event(title, db_connection, db_cursor)
    await interaction.response.send_message(f"Event '{title}' gelöscht.")


client.run(TOKEN_DISCORD)
