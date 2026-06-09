import discord
from discord import app_commands
from discord.ext import commands
from database import get_connection
from . import embeds
from . import services
from .view import EmbedBuilderView

class Comandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pool = None
    
    async def cog_load(self):
        self.pool = await get_connection()

    embed = app_commands.Group(name="embeds", description="Comandos de embeds")

    # -------------------- CRIAR EMBED --------------------
    @embed.command(name="criar", description="Cria um embed padrão.")
    @app_commands.checks.has_permissions(administrator=True)
    async def criarembed(self, interaction: discord.Interaction):

        embed_id = await services.criarembed(interaction.guild.id)

        await interaction.response.send_message(f"Embed criado com ID `{embed_id}`", embed=embeds.padrao())

    @embed.command(name="listar", description="Lista os embeds.")
    @app_commands.checks.has_permissions(administrator=True)
    async def listarembeds(self, interaction: discord.Interaction):
        embeds_list = await services.listarembeds(interaction.guild.id)

        if not embeds_list:
            await interaction.response.send_message(embed=embeds.erro("Nenhum embed criado."),ephemeral=True)
            return

        lista = "\n".join([f"ID `{e['id']}` - {e['title']}" for e in embeds_list])

        await interaction.response.send_message(embed=embeds.lista(lista))

    @embed.command(name="editar", description="Editar embed")
    @app_commands.checks.has_permissions(administrator=True)
    async def builder(self, interaction: discord.Interaction, id: int):

        data = await services.buscar_embed(interaction.guild.id, id)

        if not data:
            await interaction.response.send_message(embed=embeds.erro("Embed não encontrado."), ephemeral=True)
            return

        view = EmbedBuilderView(interaction.user)

        # carregar dados
        view.title = data["title"]
        view.description = data["description"]
        view.color = data["color"]
        view.image = data["image"]

        view.embed_id = id 

        await interaction.response.send_message(embed=view.build_embed(), view=view)

    @embed.command(name="enviar", description="Envia um embed")
    @app_commands.checks.has_permissions(administrator=True)
    async def enviar_embed(self, interaction: discord.Interaction, id: int, canal: discord.TextChannel):

        data = await services.buscar_embed(interaction.guild.id, id)

        if not data:
            await interaction.response.send_message(embed=embeds.erro("Embed não encontrado."), ephemeral=True)
            return

        embed = discord.Embed(title=data["title"], description=data["description"], color=data["color"])

        if data["image"]:
            embed.set_image(url=data["image"])

        await canal.send(embed=embed)

        await interaction.response.send_message(embed=embeds.acerto(f"✅ Embed `{id}` enviado para {canal.mention}!"))

async def setup(bot):
    await bot.add_cog(Comandos(bot))