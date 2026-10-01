import discord

from .Games import CardGame
from cogs.comercio import services as eco
from Services.database import Coins, Infos


class BlackjackView(discord.ui.View):
    """Mesa de Blackjack contra o dealer.

    Correções em relação à versão anterior: as jogadas chamavam
    ``services.draw_card()`` / ``services.calculate_hand()``, que nunca
    existiram como funções de módulo (só como métodos de ``CardGame``) —
    todo "Hit" ou "Stand" quebrava com ``AttributeError``. Também havia um
    ``self.user.id`` (deveria ser ``self.user_id``) que quebraria o "Hit"
    mesmo depois de corrigir o resto.
    """

    def __init__(self, player: list[dict], dealer: list[dict], user_id: int, aposta: int):
        super().__init__(timeout=60)
        self.player = player
        self.dealer = dealer
        self.user_id = user_id
        self.aposta = aposta
        self.get_coins = Coins.get
        self.add_coins = Coins.add
        self.message: discord.Message | None = None

    def build_embed(self, hidden: bool = True) -> discord.Embed:
        dealer_hand = (
            "?, " + ", ".join(card["display"] for card in self.dealer[1:])
            if hidden
            else ", ".join(card["display"] for card in self.dealer)
        )

        return discord.Embed(
            title="🃏 Blackjack",
            description=(
                f"💰 Aposta: **{self.aposta}**\n\n"
                f"**Sua mão:**\n"
                f"{', '.join(card['display'] for card in self.player)} "
                f"({CardGame.calculate_hand(self.player)})\n\n"
                f"**Dealer:**\n"
                f"{dealer_hand}"
            ),
            color=discord.Color.green()
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Não é seu jogo.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True

        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.player.append(CardGame.draw_card())

        if CardGame.calculate_hand(self.player) > 21:
            await self.add_coins(self.user_id, -self.aposta)
            embed = self.build_embed(hidden=False)
            embed.description += "\n💀 Você estourou!"
            self.stop()
            return await interaction.response.edit_message(embed=embed, view=None)

        await interaction.response.edit_message(embed=self.build_embed(), view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        # dealer joga
        while CardGame.calculate_hand(self.dealer) < 17:
            self.dealer.append(CardGame.draw_card())

        player_total = CardGame.calculate_hand(self.player)
        dealer_total = CardGame.calculate_hand(self.dealer)

        embed = self.build_embed(hidden=False)

        if dealer_total > 21 or player_total > dealer_total:
            embed.description += f"\n🎉 Você venceu!\n +{self.aposta} coins"
            await self.add_coins(self.user_id, self.aposta)
        elif player_total < dealer_total:
            embed.description += f"\n💀 Você perdeu!\n -{self.aposta} coins"
            await self.add_coins(self.user_id, -self.aposta)
        else:
            embed.description += "\n🤝 Empate!"

        self.stop()
        await interaction.response.edit_message(embed=embed, view=None)
