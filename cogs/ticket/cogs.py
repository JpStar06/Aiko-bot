import discord
from discord import app_commands
from discord.ext import commands
from database import get_connection
from . import services
from . import embed
from . import views

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ticket = app_commands.Group(name="ticket", description="Sistema de tickets")

    @ticket.command(name="criar", description="Cria um ticket")
    @app_commands.checks.has_permissions(administrator=True)
    async def criar_ticket(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            ticket_id = await services.criarticket(interaction.guild.id, interaction.channel.id)
            await interaction.followup.send(f"Ticket criado com ID `{ticket_id}`", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Erro ao criar ticket: {str(e)}", ephemeral=True)

    @ticket.command(name="listar", description="lista todos os tickets do server")
    @app_commands.checks.has_permissions(administrator=True)
    async def listartickets(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            tickets = await services.listarticket(interaction.guild.id)
            if not tickets:
                await interaction.followup.send("Nenhum ticket encontrado.", ephemeral=True)
                return

            ticket_list = "\n".join([f"ID `{t['id']}` - {t['titulo']}" for t in tickets])
            await interaction.followup.send(embed=embed.lista(ticket_list))
        except Exception as e:
            await interaction.followup.send(f"Erro ao listar tickets: {str(e)}", ephemeral=True)

    @ticket.command(name="editar-embeds", description=",Abre o painel de edição dos embeds (Embed 1 e Embed Cliente).",)
    @app_commands.checks.has_permissions(administrator=True)
    async def editar_embeds(self, interaction: discord.Interaction):
        data = await self.db.get_config(interaction.guild_id) or {}
 
        view = views.DualEmbedEditorView(self.db, interaction.guild_id, data)
        embed = views.build_embed_preview(data, view.current_embed)
 
        await interaction.response.send_message(
            content=f"**Editando: Embed {view.current_embed}**",
            embed=embed,
            view=view,
            ephemeral=True,
        )
        view.message = await interaction.original_response()
