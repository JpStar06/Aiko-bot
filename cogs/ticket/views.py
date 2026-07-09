"""
View responsável pelos botões:
- Alternar qual embed está sendo editado (1 ou 2)
- Abrir o modal de edição correspondente ao embed selecionado
"""

import discord
from discord import ui

from . import modals


def build_embed_preview(data: dict, embed_type: int) -> discord.Embed:
    """Monta uma pré-visualização do embed com base nos dados salvos."""
    if embed_type == 1:
        titulo = data.get("titulo") or "Sem título"
        descricao = data.get("descricao") or "Sem descrição"
        cor_hex = data.get("cor") or "#5865F2"
        imagem = data.get("imagem")
    else:
        titulo = data.get("titulo_cliente") or "Sem título"
        descricao = data.get("descricao_cliente") or "Sem descrição"
        cor_hex = data.get("cor_cliente") or "#5865F2"
        imagem = data.get("imagem_cliente")

    try:
        cor = discord.Color(int(str(cor_hex).lstrip("#"), 16))
    except (ValueError, TypeError):
        cor = discord.Color.blurple()

    embed = discord.Embed(title=titulo, description=descricao, color=cor)
    if imagem:
        embed.set_image(url=imagem)
    embed.set_footer(text=f"Pré-visualização · Embed {embed_type}")
    return embed


class DualEmbedEditorView(ui.View):
    """View com estado: sabe qual dos 2 embeds está sendo editado no momento."""

    def __init__(self, db, guild_id: int, data: dict, *, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.db = db
        self.guild_id = guild_id
        self.data = data
        self.current_embed = 1
        self.message: discord.Message | None = None
        self._atualizar_label_botao()

    def _atualizar_label_botao(self):
        proximo = 2 if self.current_embed == 1 else 1
        self.switch_button.label = f"Mudar para Embed {proximo}"

    @ui.button(label="Mudar para Embed 2", style=discord.ButtonStyle.secondary, emoji="🔁")
    async def switch_button(self, interaction: discord.Interaction, button: ui.Button):
        self.current_embed = 2 if self.current_embed == 1 else 1
        self._atualizar_label_botao()

        embed = build_embed_preview(self.data, self.current_embed)
        await interaction.response.edit_message(
            content=f"**Editando: Embed {self.current_embed}**",
            embed=embed,
            view=self,
        )

    @ui.button(label="Editar Embed", style=discord.ButtonStyle.primary, emoji="✏️")
    async def edit_button(self, interaction: discord.Interaction, button: ui.Button):
        modal = modals.EmbedEditModal(
            db=self.db,
            guild_id=self.guild_id,
            embed_type=self.current_embed,
            current_data=self.data,
        )
        modal.on_saved = self._apos_salvar
        await interaction.response.send_modal(modal)

    async def _apos_salvar(self, interaction: discord.Interaction):
        """Recarrega os dados do banco e atualiza a pré-visualização na mensagem original."""
        novos_dados = await self.db.get_config(self.guild_id)
        if novos_dados:
            self.data = novos_dados

        if self.message:
            embed = build_embed_preview(self.data, self.current_embed)
            await self.message.edit(
                content=f"**Editando: Embed {self.current_embed}**",
                embed=embed,
                view=self,
            )

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass