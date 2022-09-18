import os
import sqlite3
import time
from datetime import datetime

import discord
from discord import app_commands

TOKEN_DISCORD = os.getenv("TOKEN_DISCORD")
ID_GUILD = discord.Object(id=os.getenv("TOKEN_GUILD"))

web_links = {
    "home": "https://www.herwegh-gymnasium.de",
    "fehlzeiten": "https://www.herwegh-gymnasium.de/organisation/formulare/schueler/Entschuldigungszettel.pdf",
}

db_connection = sqlite3.connect("bot-database.db")
db_cursor = db_connection.cursor()


def get_events(cursor: sqlite3.Cursor):
    result = cursor.execute("SELECT title, description, timestamp FROM events")
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


def add_event(title: str, description: str, date: str, connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    timestamp = time.mktime(datetime.strptime(date, "%d/%m/%Y").timetuple())
    cursor.execute("INSERT INTO events (title, description, timestamp) VALUES (?, ?, ?)", (title, description, timestamp))
    connection.commit()


def del_event(title, connection: sqlite3.Connection, cursor: sqlite3.Cursor):
    cursor.execute("DELETE FROM events WHERE title=?", (title,))
    connection.commit()


class NotPermittedException(Exception):
    pass


async def check_admin_permission(interaction: discord.Interaction):
    permissions = interaction.permissions
    if not permissions.administrator:
        await interaction.response.send_message("du bist nicht dazu berechtigt, diesen Befehl auszuführen", ephemeral=True)
        raise NotPermittedException(f"'{interaction.user.name}' tried to execute '{interaction.command.name}'")


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
async def website(interaction: discord.Interaction, site: str):
    """Generiert Website Link"""
    if site in web_links:
        website_link = web_links[site]
    else:
        return "keine mögliche Option"
    await interaction.response.send_message(website_link, ephemeral=True)


@client.tree.command()
async def events(interaction: discord.Interaction):
    """Zeigt zukünftige Events an"""
    result = get_events(db_cursor)
    if result is None:
        result = "Keine Events verfügbar."
    embed = discord.Embed(title="Events", description=result, colour=discord.Color.green())
    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command()
@app_commands.rename(title="titel")
@app_commands.rename(description="beschreibung")
@app_commands.rename(date="datum")
@app_commands.describe(date="(01/01/2000)")
async def addevent(interaction: discord.Interaction, title: str, description: str, date: str):
    """Erstellt Event"""
    try:
        await check_admin_permission(interaction)
    except NotPermittedException as e:
        print(e)    #TODO implement logging
        return
    add_event(title, description, date, db_connection, db_cursor)
    await interaction.response.send_message(f"Event '{title}' erstellt.")


@client.tree.command()
@app_commands.rename(title="titel")
async def delevent(interaction: discord.Interaction, title: str):
    """Löscht Event"""
    try:
        await check_admin_permission(interaction)
    except NotPermittedException as e:
        print(e)    #TODO implement logging
        return
    del_event(title, db_connection, db_cursor)
    await interaction.response.send_message(f"Event '{title}' gelöscht.")


client.run(TOKEN_DISCORD)
