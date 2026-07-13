import discord


class TitleModal(discord.ui.Modal, title="Editar Título"):
    novo_titulo = discord.ui.TextInput(label="Novo título")

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        self.view.title = self.novo_titulo.value

        await interaction.response.edit_message(
            embed=self.view.build_embed(),
            view=self.view
        )


class DescModal(discord.ui.Modal, title="Editar Descrição"):
    descricao = discord.ui.TextInput(
        label="Descrição",
        style=discord.TextStyle.paragraph
    )

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        self.view.description = self.descricao.value

        await interaction.response.edit_message(
            embed=self.view.build_embed(),
            view=self.view
        )


class ColorModal(discord.ui.Modal, title="Editar Cor"):
    cor = discord.ui.TextInput(
        label="Cor (hex)",
        placeholder="#3498db"
    )

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):
        try:
            value = int(self.cor.value.replace("#", ""), 16)
            self.view.color = discord.Color(value)
        except:
            await interaction.response.send_message(
                "❌ Cor inválida!",
                ephemeral=True
            )
            return

        await interaction.response.edit_message(
            embed=self.view.build_embed(),
            view=self.view
        )


class ImageModal(discord.ui.Modal, title="Imagem"):
    url = discord.ui.TextInput(label="URL da imagem")

    def __init__(self, view):
        super().__init__()
        self.view = view

    async def on_submit(self, interaction: discord.Interaction):

        if not self.url.value.startswith("http"):
            await interaction.response.send_message(
                "❌ URL inválida!",
                ephemeral=True
            )
            return

        self.view.image = self.url.value

        await interaction.response.edit_message(
            embed=self.view.build_embed(),
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

        value = self.cargo.value.replace("<@&", "").replace(">", "")

        try:
            role_id = int(value)
        except:
            await interaction.response.send_message(
                "❌ Cargo inválido!",
                ephemeral=True
            )
            return

        role = interaction.guild.get_role(role_id)

        if not role:
            await interaction.response.send_message(
                "❌ Cargo não encontrado!",
                ephemeral=True
            )
            return

        self.view.staff_role = role
        self.view.staff_id = role.id

        await interaction.response.edit_message(
            embed=self.view.build_embed(),
            view=self.view
        )