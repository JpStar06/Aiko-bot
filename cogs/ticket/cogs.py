import discord
from discord import app_commands
from discord.ext import commands

from . import services
from . import embeds
from .view import TicketBuilderView
from .view import TicketOpenView


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    tickets = app_commands.Group(
        name="tickets",
        description="Comandos de tickets"
    )

    # -------------------- CRIAR -------------------- #
    @tickets.command(name="criar", description="cria um ticket padrão")
    @app_commands.checks.has_permissions(administrator=True)
    async def criarticket(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        try:
            ticket_id = await services.criarticket(
                interaction.guild.id,
                interaction.channel.id
            )

            await interaction.followup.send(
                content=f"✅ Ticket criado com ID `{ticket_id}`",
                embed=embeds.padrao()
            )

        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}")

    # -------------------- LISTAR -------------------- #
    @tickets.command(name="listar", description="lista todos os tickets do server")
    @app_commands.checks.has_permissions(administrator=True)
    async def listartickets(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        try:
            ticketlist = await services.listarticket(interaction.guild.id)

            if not ticketlist:
                await interaction.followup.send(
                    embed=embeds.erro("Nenhum ticket criado.")
                )
                return

            lista = "\n".join(
                [f"ID `{e['id']}` - {e['titulo']}" for e in ticketlist]
            )

            await interaction.followup.send(
                embed=embeds.lista(lista)
            )

        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}")

    # -------------------- EDITAR -------------------- #
    @tickets.command(name="editar", description="editar um ticket")
    @app_commands.checks.has_permissions(administrator=True)
    async def builder(self, interaction: discord.Interaction, id: int):

        await interaction.response.defer()  # 👈 ESSENCIAL

        try:
            data = await services.buscar_ticket(
                interaction.guild.id,
                id
            )

            if not data:
                return await interaction.followup.send(
                    embed=embeds.erro("ticket não encontrado."),
                    ephemeral=True
                )

            view = TicketBuilderView(interaction.user, id)

            # carregar dados
            view.title = data["title"]
            view.description = data["description"]
            view.color = discord.Color(data["color"])
            view.image = data["image"]

            # 👮 carregar staff
            view.staff_id = data["staff_id"]
            if data["staff_id"]:
                role = interaction.guild.get_role(data["staff_id"])
                if role:
                    view.staff_role = role

            await interaction.followup.send(
                embed=view.build_embed(),
                view=view
            )

        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}")
    # -------------------- ENVIAR -------------------- #
    @tickets.command(name="enviar", description="envia o ticket para um canal")
    @app_commands.checks.has_permissions(administrator=True)
    async def enviar_ticket(
        self,
        interaction: discord.Interaction,
        id: int,
        canal: discord.TextChannel
    ):

        await interaction.response.defer(ephemeral=True)

        try:
            data = await services.buscar_ticket(
                interaction.guild.id,
                id
            )

            if not data:
                await interaction.followup.send(
                    embed=embeds.erro("Ticket não encontrado.")
                )
                return

            embed = discord.Embed(
                title=data["title"],
                description=data["description"],
                color=discord.Color(data["color"])
            )

            if data["image"]:
                embed.set_image(url=data["image"])

            await canal.send(embed=embed, view=TicketOpenView(id))

            await interaction.followup.send(
                embed=embeds.acerto(
                    f"✅ Ticket `{id}` enviado para {canal.mention}!"
                )
            )

        except Exception as e:
            await interaction.followup.send(f"❌ Erro: {e}")


# -------------------- SETUP -------------------- #
async def setup(bot):
    await bot.add_cog(Tickets(bot))