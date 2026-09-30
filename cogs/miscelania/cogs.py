import discord
import random
from discord import app_commands
from discord.ext import commands
from databaseConfig import get_connection
from . import services
from . import embeds

class Mis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    play = app_commands.Group(name="play", description= "jogos")

    @play.command(name="8ball", description="Faça uma pergunta para a bola mágica")
    async def eightball(self, interaction: discord.Interaction, pergunta: str):
        
        itens = [
            "Sim.",
            "Não.",
            "Talvez.",
            "Com certeza.",
            "Pergunte novamente depois.",
            "Muito improvável.",
            "Definitivamente."
        ]
        resposta = random.choice(itens)

        await interaction.response.send_message(embed=embeds.ball(f"Pergunta: {pergunta}\nResposta: {resposta}"))

async def setup(bot):
    await bot.add_cog(Mis(bot))