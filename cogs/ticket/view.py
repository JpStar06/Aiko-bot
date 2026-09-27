import asyncio
import io

import discord

from . import services
from .modals import CampoTextoModal, CorModal, ImagemModal, StaffModal

CATEGORIA_TICKETS = "Tickets"
CANAL_LOGS = "logs-tickets"


class TicketBuilderView(discord.ui.View):
    """Editor com dois embeds: o do painel (mensagem pública) e o do cliente
    (mensagem enviada dentro do canal quando o ticket é aberto)."""

    def __init__(self, author: discord.abc.User, ticket_id: int):
        super().__init__(timeout=None)

        self.author = author
        self.ticket_id = ticket_id

        # embed do painel
        self.title = "Título"
        self.description = "Descrição"
        self.color = discord.Color.blue()
        self.image = None

        # embed exibido ao cliente quando o ticket é aberto
        self.title_cliente = "ESPERE SER ATENDIDO"
        self.description_cliente = "Nossa equipe pode estar ocupada."
        self.color_cliente = discord.Color.red()
        self.image_cliente = None

        self.staff_role: discord.Role | None = None
        self.staff_id: int | None = None

    # -------------------- EMBEDS -------------------- #
    def build_embeds(self) -> list[discord.Embed]:
        painel = discord.Embed(
            title=self.title,
            description=self.description,
            color=self.color,
        )
        painel.set_footer(text="📋 Embed do painel (mensagem pública)")

        if self.image:
            painel.set_image(url=self.image)

        if self.staff_role:
            painel.add_field(name="👮 Atendente", value=self.staff_role.mention, inline=False)

        cliente = discord.Embed(
            title=self.title_cliente,
            description=self.description_cliente,
            color=self.color_cliente,
        )
        cliente.set_footer(text="📨 Embed enviado ao abrir o ticket")

        if self.image_cliente:
            cliente.set_image(url=self.image_cliente)

        return [painel, cliente]

    # -------------------- PERMISSÃO -------------------- #
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("❌ Você não pode usar isso.", ephemeral=True)
            return False
        return True

    # -------------------- EMBED DO PAINEL -------------------- #
    @discord.ui.button(label="✏️ Título", style=discord.ButtonStyle.primary, row=0)
    async def editar_titulo(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            CampoTextoModal(self, titulo_modal="Editar Título do Painel", atributo="title", label="Novo título")
        )

    @discord.ui.button(label="📝 Descrição", style=discord.ButtonStyle.secondary, row=0)
    async def editar_desc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            CampoTextoModal(
                self, titulo_modal="Editar Descrição do Painel", atributo="description",
                label="Descrição", paragrafo=True
            )
        )

    @discord.ui.button(label="🎨 Cor", style=discord.ButtonStyle.success, row=0)
    async def editar_cor(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            CorModal(self, titulo_modal="Editar Cor do Painel", atributo="color")
        )

    @discord.ui.button(label="🖼️ Imagem", style=discord.ButtonStyle.secondary, row=0)
    async def editar_img(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            ImagemModal(self, titulo_modal="Imagem do Painel", atributo="image")
        )

    @discord.ui.button(label="👮 Atendente", style=discord.ButtonStyle.secondary, row=0)
    async def editar_staff(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StaffModal(self))

    # -------------------- EMBED DO CLIENTE -------------------- #
    @discord.ui.button(label="✏️ Título (ticket)", style=discord.ButtonStyle.primary, row=1)
    async def editar_titulo_cliente(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            CampoTextoModal(
                self, titulo_modal="Editar Título (ticket)", atributo="title_cliente", label="Novo título"
            )
        )

    @discord.ui.button(label="📝 Descrição (ticket)", style=discord.ButtonStyle.secondary, row=1)
    async def editar_desc_cliente(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            CampoTextoModal(
                self, titulo_modal="Editar Descrição (ticket)", atributo="description_cliente",
                label="Descrição", paragrafo=True
            )
        )

    @discord.ui.button(label="🎨 Cor (ticket)", style=discord.ButtonStyle.success, row=1)
    async def editar_cor_cliente(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            CorModal(self, titulo_modal="Editar Cor (ticket)", atributo="color_cliente")
        )

    @discord.ui.button(label="🖼️ Imagem (ticket)", style=discord.ButtonStyle.secondary, row=1)
    async def editar_img_cliente(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            ImagemModal(self, titulo_modal="Imagem (ticket)", atributo="image_cliente")
        )

    # -------------------- SALVAR -------------------- #
    @discord.ui.button(label="💾 Salvar", style=discord.ButtonStyle.green, row=2)
    async def salvar(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await services.editar_ticket(
                interaction.guild.id,
                self.ticket_id,
                self.title,
                self.description,
                self.color.value,
                self.image,
                self.staff_id,
                self.title_cliente,
                self.description_cliente,
                self.color_cliente.value,
                self.image_cliente,
            )

            await interaction.response.send_message(
                f"✅ Ticket `{self.ticket_id}` atualizado!", ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao salvar: {e}", ephemeral=True)


class TicketOpenView(discord.ui.View):
    """Painel público com o botão que abre um canal de ticket privado.

    O ``custom_id`` do botão inclui o ``ticket_id`` para que múltiplos
    painéis no mesmo servidor (ou em servidores diferentes) continuem
    funcionando de forma independente após o bot reiniciar.
    """

    def __init__(self, ticket_id: int):
        super().__init__(timeout=None)
        self.ticket_id = ticket_id

        botao = discord.ui.Button(
            label="🎫 Abrir Ticket",
            style=discord.ButtonStyle.green,
            custom_id=f"ticket_open:{ticket_id}",
        )
        botao.callback = self.abrir_ticket
        self.add_item(botao)

    async def abrir_ticket(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        data = await services.buscar_ticket(guild.id, self.ticket_id)

        if not data:
            return await interaction.response.send_message(
                "❌ Configuração de ticket não encontrada.", ephemeral=True
            )

        # 🚫 evitar duplicação (por painel, um usuário pode ter só um ticket aberto)
        if await services.usuario_tem_ticket_aberto(guild.id, self.ticket_id, user.id):
            return await interaction.response.send_message(
                "❌ Você já tem um ticket aberto para este painel.", ephemeral=True
            )

        staff_role = guild.get_role(data["staff_id"]) if data["staff_id"] else None

        category = discord.utils.get(guild.categories, name=CATEGORIA_TICKETS)
        if not category:
            category = await guild.create_category(CATEGORIA_TICKETS)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            ),
        }

        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            )

        try:
            channel = await guild.create_text_channel(
                name=f"ticket-{self.ticket_id}-{user.id}",
                category=category,
                overwrites=overwrites,
            )

            embed = discord.Embed(
                title=data["title_cliente"] or data["title"],
                description=data["description_cliente"] or data["description"],
                color=discord.Color(data["color_cliente"] if data["color_cliente"] is not None else data["color"]),
            )

            imagem = data["image_cliente"] or data["image"]
            if imagem:
                embed.set_image(url=imagem)

            await channel.send(
                content=f"{user.mention}" + (f" {staff_role.mention}" if staff_role else ""),
                embed=embed,
                view=CloseTicketView(),
            )

            await services.registrar_canal_ticket(
                channel.id, self.ticket_id, guild.id, user.id,
                staff_role.id if staff_role else None,
            )

            await interaction.response.send_message(
                f"✅ Ticket criado: {channel.mention}", ephemeral=True
            )

        except Exception as e:
            await interaction.response.send_message(f"❌ Erro ao criar ticket: {e}", ephemeral=True)


class CloseTicketView(discord.ui.View):
    """Botão de fechar ticket. Uma única instância/``custom_id`` serve para
    todos os canais — quem pode ou não fechar é resolvido em tempo real
    consultando o dono/staff do canal atual, então não precisa de estado
    por instância nem de recriação especial após reiniciar o bot."""

    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.guild_permissions.administrator:
            return True

        info = await services.buscar_canal_ticket(interaction.channel.id)

        if info:
            dono = interaction.user.id == info["user_id"]
            staff = info["staff_id"] and any(r.id == info["staff_id"] for r in interaction.user.roles)
            if dono or staff:
                return True

        await interaction.response.send_message(
            "❌ Você não tem permissão para fechar este ticket.", ephemeral=True
        )
        return False

    @discord.ui.button(
        label="❌ Fechar Ticket",
        style=discord.ButtonStyle.red,
        custom_id="close_ticket",
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
                content += " " + " ".join(a.url for a in msg.attachments)

            messages.append(f"[{timestamp}] {msg.author}: {content}")

        transcript_text = "\n".join(messages)

        file = discord.File(
            io.BytesIO(transcript_text.encode()),
            filename=f"transcript-{channel.name}.txt",
        )

        try:
            await interaction.user.send(f"📄 Transcript do ticket `{channel.name}`", file=file)
        except discord.Forbidden:
            pass

        log_channel = discord.utils.get(channel.guild.text_channels, name=CANAL_LOGS)
        if log_channel:
            file.reset()
            await log_channel.send(
                f"📄 Ticket `{channel.name}` fechado por {interaction.user.mention}", file=file
            )

        await services.remover_canal_ticket(channel.id)

        await interaction.followup.send("🗑 Fechando ticket em 3 segundos...")
        await asyncio.sleep(3)
        await channel.delete()
