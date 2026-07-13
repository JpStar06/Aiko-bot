import discord
from datetime import datetime
import io
import asyncio
from .modals import (
    TitleModal,
    DescModal,
    ColorModal,
    ImageModal,
    StaffModal
)
from . import services


class TicketBuilderView(discord.ui.View):
    def __init__(self, author, ticket_id: int):
        super().__init__(timeout=None)

        self.author = author
        self.ticket_id = ticket_id

        self.title = "Título"
        self.description = "Descrição"
        self.color = discord.Color.blue()
        self.image = None

        self.staff_role = None
        self.staff_id = None

    # -------------------- EMBED -------------------- #
    def build_embed(self):
        embed = discord.Embed(
            title=self.title,
            description=self.description,
            color=self.color
        )

        if self.image:
            embed.set_image(url=self.image)

        if self.staff_role:
            embed.add_field(
                name="👮 Atendente",
                value=self.staff_role.mention,
                inline=False
            )

        return embed

    # -------------------- PERMISSÃO -------------------- #
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.author:
            await interaction.response.send_message(
                "❌ Você não pode usar isso.",
                ephemeral=True
            )
            return False
        return True

    # -------------------- BOTÕES -------------------- #

    @discord.ui.button(label="✏️ Título", style=discord.ButtonStyle.primary)
    async def editar_titulo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TitleModal(self))

    @discord.ui.button(label="📝 Descrição", style=discord.ButtonStyle.secondary)
    async def editar_desc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DescModal(self))

    @discord.ui.button(label="🎨 Cor", style=discord.ButtonStyle.success)
    async def editar_cor(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ColorModal(self))

    @discord.ui.button(label="🖼️ Imagem", style=discord.ButtonStyle.secondary)
    async def editar_img(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ImageModal(self))

    @discord.ui.button(label="👮 Atendente", style=discord.ButtonStyle.secondary)
    async def editar_staff(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StaffModal(self))

    # -------------------- SALVAR -------------------- #
    @discord.ui.button(label="💾 Salvar", style=discord.ButtonStyle.green)
    async def salvar(self, interaction: discord.Interaction, button: discord.ui.Button):

        try:
            await services.editar_ticket(
                interaction.guild.id,
                self.ticket_id,
                self.title,
                self.description,
                self.color.value,  # 👈 salva como int
                self.image,
                self.staff_id  # 👈 salva staff
            )

            await interaction.response.send_message(
                f"✅ Ticket `{self.ticket_id}` atualizado!",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro ao salvar: {e}",
                ephemeral=True
            )

class TicketOpenView(discord.ui.View):
    def __init__(self, ticket_id: int):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

    @discord.ui.button(
        label="🎫 Abrir Ticket",
        style=discord.ButtonStyle.green,
        custom_id="ticket_open_private"
    )
    async def abrir_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        # 🔍 buscar config do ticket
        data = await services.buscar_ticket(guild.id, self.ticket_id)

        if not data:
            return await interaction.response.send_message(
                "❌ Configuração de ticket não encontrada.",
                ephemeral=True
            )

        # 🚫 evitar duplicação
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{user.id}")
        if existing:
            return await interaction.response.send_message(
                f"❌ Você já tem um ticket aberto: {existing.mention}",
                ephemeral=True
            )

        # 👮 pegar cargo staff
        staff_role = None
        if data["staff_id"]:
            staff_role = guild.get_role(data["staff_id"])

        # 📁 categoria (cria se não existir)
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            category = await guild.create_category("Tickets")

        # 🔒 permissões
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
        }

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )

        try:
            # 📦 criar canal
            channel = await guild.create_text_channel(
                name=f"ticket-{user.id}",
                category=category,
                overwrites=overwrites
            )

            # 📩 embed do ticket
            embed = discord.Embed(
                title=data["title"],
                description=data["description"],
                color=discord.Color(data["color"])
            )

            if data["image"]:
                embed.set_image(url=data["image"])

            await channel.send(
                content=f"{user.mention}" + (f" {staff_role.mention}" if staff_role else ""),
                embed=embed,
                view=CloseTicketView()
            )

            await interaction.response.send_message(
                f"✅ Ticket criado: {channel.mention}",
                ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro ao criar ticket: {e}",
                ephemeral=True
            )

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="❌ Fechar Ticket",
        style=discord.ButtonStyle.red,
        custom_id="close_ticket"
    )
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel

        # 🧾 gerar transcript
        messages = []
        async for msg in channel.history(limit=None, oldest_first=True):
            timestamp = msg.created_at.strftime("%d/%m/%Y %H:%M")
            content = msg.content or ""

            if msg.attachments:
                content += " " + " ".join([a.url for a in msg.attachments])

            messages.append(f"[{timestamp}] {msg.author}: {content}")

        transcript_text = "\n".join(messages)

        file = discord.File(
            io.BytesIO(transcript_text.encode()),
            filename=f"transcript-{channel.name}.txt"
        )

        try:
            # 👤 manda no privado de quem clicou
            await interaction.user.send(
                f"📄 Transcript do ticket `{channel.name}`",
                file=file
            )
        except:
            pass

        # 📢 opcional: log em canal
        log_channel = discord.utils.get(channel.guild.text_channels, name="logs-tickets")
        if log_channel:
            await log_channel.send(
                f"📄 Ticket `{channel.name}` fechado por {interaction.user.mention}",
                file=file
            )

        # ⏳ aviso antes de deletar
        await interaction.followup.send("🗑 Fechando ticket em 3 segundos...")

        await asyncio.sleep(3)

        await channel.delete()