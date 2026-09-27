import discord


def erro(msg: str):
    return discord.Embed(
        title="❌ Erro",
        description=msg,
        color=discord.Color.red()
    )


def ganhou(msg: str):
    return discord.Embed(
        title="🎉 GANHOU!",
        description=msg,
        color=discord.Color.green()
    )


def perdeu(msg: str):
    return discord.Embed(
        title="💀 PERDEU!",
        description=msg,
        color=discord.Color.red()
    )


def empate(msg: str):
    return discord.Embed(
        title="🤝 EMPATE",
        description=msg,
        color=discord.Color.greyple()
    )
