import lightbulb
import configparser
import sqlite3
import time
from datetime import datetime

config = configparser.ConfigParser()
config.read("config.ini")
token_dicord = config["DEFAULT"]["token_discord"]

bot = lightbulb.BotApp(token=token_dicord)

web_links = {
    "home": "https://www.herwegh-gymnasium.de",
    "fehlzeiten": "https://www.herwegh-gymnasium.de/organisation/formulare/schueler/Entschuldigungszettel.pdf",
}

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
                column = "*" + column + "*"
            res_str += column
            res_str += " "
            i += 1
        res_str += "\n"
        i = 0
    
    return res_str

def add_event(title:str, description:str, date:str, con, cur):
    timestamp = time.mktime(datetime.strptime(date, "%d/%m/%Y").timetuple())
    cur.execute(f"INSERT INTO events (title, description, timestamp) VALUES (?, ?, ?)", (title, description, timestamp))
    con.commit()
    
def del_event(title, con, cur):
    cur.execute(f"DELETE FROM events WHERE title=?", (title))
    con.commit()
    

@bot.command
@lightbulb.option("seite", "/help für info", type=str)
@lightbulb.command("website", "Generiert Website Link")
@lightbulb.implements(lightbulb.SlashCommand)
async def website(ctx):
    if ctx.options.seite in web_links:
        website_link = web_links[ctx.options.seite]
    else:
        return "keine mögliche Option"
    await ctx.respond(website_link)


@bot.command
@lightbulb.command("events", "Zeigt zukünftige Events an")
@lightbulb.implements(lightbulb.SlashCommand)
async def events(ctx):
    response = get_events(cur)
    await ctx.respond(response)

@bot.command
@lightbulb.option("title", "Event Titel", type=str)
@lightbulb.option("description", "Event Beschreibung", type=str)
@lightbulb.option("date", "Event Datum (Format: 01/01/2000))", type=str)
@lightbulb.command("addevent", "Fügt Event hinzu")
@lightbulb.implements(lightbulb.SlashCommand)
async def addevent(ctx):
    add_event(ctx.options.title, ctx.options.description, ctx.options.date, con, cur)

@bot.command
@lightbulb.option("title", "Event Titel", type=str)
@lightbulb.command("delevent", "Löscht Event")
@lightbulb.implements(lightbulb.SlashCommand)
async def delevent(ctx):
    del_event(ctx.options.title, con, cur)
    await ctx.respond(f"Event '{ctx.options.title}' gelöscht")

@bot.command
@lightbulb.command("help", "hilfe zu commands")
@lightbulb.implements(lightbulb.SlashCommand)
async def help(ctx):
    response = """
    /website:
    \u2022 home: Homepage
    \u2022 fehlzeiten: Fehlzeiten Formular
    """
    await ctx.respond(response)

bot.run()
