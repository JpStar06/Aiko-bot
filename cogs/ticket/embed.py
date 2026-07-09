import discord

def lista(msg: str):
    return discord.Embed(
        title="LISTA DE TICKETS",
        description=msg,
        color=discord.Color.yellow()
    )