"""
Modal único que edita 2 embeds diferentes, dependendo do "embed_type" (1 ou 2).
Discord limita modais a 5 TextInput, então cada embed usa exatamente 5 campos.
"""

import discord
from discord import ui

# Definição dos campos de cada embed.
# Embed 1 -> campos "normais". Embed 2 -> campos com sufixo "_cliente".
CAMPOS_EMBED = {
    1: {
        "titulo": {"label": "Título", "style": discord.TextStyle.short, "max_length": 256},
        "descricao": {"label": "Descrição", "style": discord.TextStyle.paragraph, "max_length": 4000},
        "cor": {"label": "Cor (hex, ex: #5865F2)", "style": discord.TextStyle.short, "max_length": 7},
        "imagem": {"label": "URL da Imagem", "style": discord.TextStyle.short, "max_length": 300},
        "emoji": {"label": "Emoji", "style": discord.TextStyle.short, "max_length": 100},
    },
    2: {
        "titulo_cliente": {"label": "Título (Cliente)", "style": discord.TextStyle.short, "max_length": 256},
        "descricao_cliente": {"label": "Descrição (Cliente)", "style": discord.TextStyle.paragraph, "max_length": 4000},
        "cor_cliente": {"label": "Cor (hex, ex: #5865F2)", "style": discord.TextStyle.short, "max_length": 7},
        "imagem_cliente": {"label": "URL da Imagem (Cliente)", "style": discord.TextStyle.short, "max_length": 300},
        "mensagem_cliente": {"label": "Mensagem (Cliente)", "style": discord.TextStyle.paragraph, "max_length": 1000},
    },
}


class EmbedEditModal(ui.Modal):
    """Modal dinâmico: monta os campos de acordo com embed_type (1 ou 2)."""

    def __init__(self, db, guild_id: int, embed_type: int, current_data: dict):
        super().__init__(title=f"Editar Embed {embed_type}")
        self.db = db
        self.guild_id = guild_id
        self.embed_type = embed_type
        self.on_saved = None  # callback opcional, definido por quem cria o modal

        self.inputs: dict[str, ui.TextInput] = {}
        campos = CAMPOS_EMBED[embed_type]

        for nome_campo, cfg in campos.items():
            valor_atual = current_data.get(nome_campo) or ""
            text_input = ui.TextInput(
                label=cfg["label"],
                style=cfg["style"],
                max_length=cfg.get("max_length", 256),
                required=False,
                default=str(valor_atual),
            )
            self.inputs[nome_campo] = text_input
            self.add_item(text_input)

    async def on_submit(self, interaction: discord.Interaction):
        valores = {nome: (campo.value or None) for nome, campo in self.inputs.items()}
        await self.db.update_many(self.guild_id, valores)

        await interaction.response.send_message(
            f"✅ Embed {self.embed_type} atualizado com sucesso!", ephemeral=True
        )

        if self.on_saved is not None:
            await self.on_saved(interaction)

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        await interaction.response.send_message(
            f"❌ Ocorreu um erro ao salvar: {error}", ephemeral=True
        )