"""
Modais usados pelo editor de tickets (:class:`TicketBuilderView`).

Antes havia uma classe quase idêntica por campo/embed (título do painel,
título do cliente, etc). Aqui os campos de texto e de cor são genéricos:
recebem qual atributo da view devem alterar, então servem tanto para o
embed do painel quanto para o embed exibido ao cliente dentro do ticket.
"""

import discord


class CampoTextoModal(discord.ui.Modal):
    """Edita um único campo de texto (título ou descrição) de qualquer embed da view."""

    def __init__(
        self,
        view,
        *,
        titulo_modal: str,
        atributo: str,
        label: str,
        paragrafo: bool = False,
    ):
        super().__init__(title=titulo_modal)
        self.view = view
        self.atributo = atributo

        valor_atual = getattr(view, atributo, None)

        self.campo = discord.ui.TextInput(
            label=label,
            style=discord.TextStyle.paragraph if paragrafo else discord.TextStyle.short,
            default=valor_atual,
            max_length=4000 if paragrafo else 256,
        )
        self.add_item(self.campo)

    async def on_submit(self, interaction: discord.Interaction):
        setattr(self.view, self.atributo, self.campo.value)

        await interaction.response.edit_message(
            embeds=self.view.build_embeds(),
            view=self.view
        )


class CorModal(discord.ui.Modal):
    """Edita a cor (hex) de qualquer embed da view."""

    def __init__(self, view, *, titulo_modal: str, atributo: str):
        super().__init__(title=titulo_modal)
        self.view = view
        self.atributo = atributo

        valor_atual = getattr(view, atributo, None)
        default = f"#{valor_atual.value:06X}" if isinstance(valor_atual, discord.Color) else None

        self.cor = discord.ui.TextInput(
            label="Cor (hex)",
            placeholder="#3498db",
            default=default,
        )
        self.add_item(self.cor)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            valor = int(self.cor.value.replace("#", ""), 16)
        except ValueError:
            await interaction.response.send_message("❌ Cor inválida!", ephemeral=True)
            return

        setattr(self.view, self.atributo, discord.Color(valor))

        await interaction.response.edit_message(
            embeds=self.view.build_embeds(),
            view=self.view
        )


class ImagemModal(discord.ui.Modal):
    """Edita a URL de imagem de qualquer embed da view."""

    def __init__(self, view, *, titulo_modal: str, atributo: str):
        super().__init__(title=titulo_modal)
        self.view = view
        self.atributo = atributo

        self.url = discord.ui.TextInput(
            label="URL da imagem",
            default=getattr(view, atributo, None),
            required=False,
        )
        self.add_item(self.url)

    async def on_submit(self, interaction: discord.Interaction):
        valor = self.url.value.strip()

        if valor and not valor.startswith("http"):
            await interaction.response.send_message("❌ URL inválida!", ephemeral=True)
            return

        setattr(self.view, self.atributo, valor or None)

        await interaction.response.edit_message(
            embeds=self.view.build_embeds(),
            view=self.view
        )


class StaffModal(discord.ui.Modal, title="Definir cargo staff"):
    cargo = discord.ui.TextInput(
        label="ID do cargo ou @menção",
        placeholder="@Staff ou 123456789"
    )

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        valor = self.cargo.value.replace("<@&", "").replace(">", "").strip()

        try:
            role_id = int(valor)
        except ValueError:
            await interaction.response.send_message("❌ Cargo inválido!", ephemeral=True)
            return

        role = interaction.guild.get_role(role_id)

        if not role:
            await interaction.response.send_message("❌ Cargo não encontrado!", ephemeral=True)
            return

        self.view.staff_role = role
        self.view.staff_id = role.id

        await interaction.response.edit_message(
            embeds=self.view.build_embeds(),
            view=self.view
        )
