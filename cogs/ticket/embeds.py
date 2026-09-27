import discord


def padrao():
    return discord.Embed(
        title="Título do Embed",
        description="use /embed editar para editar os embeds",
        color=discord.Color.blue()
    )


def erro(msg: str):
    return discord.Embed(
        title="❌ Erro",
        description=msg,
        color=discord.Color.red()
    )


def acerto(msg: str):
    return discord.Embed(
        title="✅ Concluído",
        description=msg,
        color=discord.Color.green()
    )


def lista(msg: str):
    return discord.Embed(
        title="🎫 Tickets criados",
        description=msg,
        color=discord.Color.purple()
    )
