import lightbulb
import configparser

import time
import datetime

config = configparser.ConfigParser()
config.read("config.ini")
token_dicord = config["DEFAULT"]["token_discord"]

bot = lightbulb.BotApp(token=token_dicord)

web_links = {
    "home": "https://www.herwegh-gymnasium.de",
    "fehlzeiten": "https://www.herwegh-gymnasium.de/organisation/formulare/schueler/Entschuldigungszettel.pdf",
}

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
