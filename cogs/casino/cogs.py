import discord
import random
from discord import app_commands
from discord.ext import commands
from database import get_connection
from . import services, embeds, views
from cogs.comercio import services as eco

class Casino(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_coins = eco.get_coins
        self.add_coins = eco.add_coins
        self.get_user = eco.get_user

    casino = app_commands.Group(name="casino", description="Jogos de aposta")

    # -------------------- COINFLIP --------------------
    @casino.command(name="coinflip", description="Cara ou coroa")
    @app_commands.checks.cooldown(1, 2)
    async def coinflip(self, interaction: discord.Interaction, aposta: int, escolha: str):
        coins = await self.get_coins(interaction.user.id)
        game = services.CoinFlipGame()
        sucesso, resultado = game.play(escolha, aposta, coins)

        if not sucesso:
            await interaction.response.send_message(embed=embeds(f"ops, algo deu errado\n{resultado}"))
            return

        if resultado["venceu"]:
            await self.add_coins(interaction.user.id, aposta)
            embedresult = embeds.ganhou(f"você perdeu{resultado[1]}")
        else:
            await self.add_coins(interaction.user.id, -aposta)
            embedresult = embeds.perdeu(f"você perdeu{resultado[1]}")

        await interaction.response.send_message(embed=embedresult)

    @coinflip.error
    async def coinflip_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.CommandOnCooldown):
            if interaction.response.is_done():
                await interaction.followup.send(
                    embed=embeds.erro(f"⏳ Espere {round(error.retry_after)} segundos para usar novamente."),
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    embed=embeds.erro(f"⏳ Espere {round(error.retry_after)} segundos para usar novamente."),
                    ephemeral=True
                )
    #-----------dices-----------------------
    @casino.command(name="dice", description="Jogue dados")
    @app_commands.checks.cooldown(1, 6)
    async def dice(self, interaction: discord.Interaction, aposta: int):
        coins = await self.get_coins(interaction.user.id)
        if aposta > coins:
            await interaction.response.send_message(embed=embeds.erro("Você não tem coins suficientes."), ephemeral=True)
            return
        
        if aposta <= 0:
            await interaction.response.send_message(embed=embeds.erro("Você não pode usar valor igual ou menor que 0."), ephemeral=True)
            return

        player = random.randint(1, 6)
        bot_roll = random.randint(1, 6)

        if player > bot_roll:
            await self.add_coins(interaction.user.id, aposta)
            embedresult = embeds.ganhou(f"🎲 Você: {player}\n🎲 Bot: {bot_roll}\nVocê ganhou `{aposta}` coins!")
        elif player < bot_roll:
            await self.add_coins(interaction.user.id, -aposta)
            embedresult = embeds.perdeu(f"🎲 Você: {player}\n🎲 Bot: {bot_roll}\nVocê perdeu `{aposta}` coins.")
        else:
            embedresult = embeds.ganhou(f"🎲 Você: {player}\n🎲 Bot: {bot_roll}\nEmpate!")

        await interaction.response.send_message(embed=embedresult)

    @dice.error
    async def dice_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.CommandOnCooldown):
            if interaction.response.is_done():
                await interaction.followup.send(
                    embed=embeds.erro(f"⏳ Espere {round(error.retry_after)} segundos para usar novamente."),
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    embed=embeds.erro(f"⏳ Espere {round(error.retry_after)} segundos para usar novamente."),
                    ephemeral=True
                )

#---------------------SLOTS----------------------
    @casino.command(name="slots", description="Caça-níquel")
    @app_commands.checks.cooldown(1, 6)
    async def slots(self, interaction: discord.Interaction, aposta: int):
        coins = await self.get_coins(interaction.user.id)
        if aposta > coins:
            await interaction.response.send_message(embed=embeds.erro("Você não tem coins suficientes."), ephemeral=True)
            return
        
        if aposta <= 0:
            await interaction.response.send_message(embed=embeds.erro("Você não pode usar valor igual ou menor que 0."), ephemeral=True)
            return
        
        (r1, r2, r3), ganho, tipo = services.SlotGame.spin_slots(aposta)
        resultado = f"{r1} | {r2} | {r3}\n"

        if tipo == "jackpot":
            embed = embeds.ganhou(resultado + f"🎉 JACKPOT! Você ganhou `{ganho}` coins!")
        elif tipo == "lose":
            embed = embeds.perdeu(resultado + f"❌ LOSE! Você perdeu `{ganho}` coins!")
        else:
            embed = embeds.ganhou(resultado + f"✨ Você ganhou `{ganho}` coins!")

        await self.add_coins(interaction.user.id, ganho)
        await interaction.response.send_message(embed=embed)
    
    @slots.error
    async def slots_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.CommandOnCooldown):
            if interaction.response.is_done():
                await interaction.followup.send(
                    embed=embeds.erro(f"⏳ Espere {round(error.retry_after)} segundos para usar novamente."),
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    embed=embeds.erro(f"⏳ Espere {round(error.retry_after)} segundos para usar novamente."),
                    ephemeral=True
                )
    
    @casino.command(name="blackjack", description="Jogar blackjack")
    async def blackjack(self, interaction: discord.Interaction, aposta: int):

        await interaction.response.defer()  # 👈 ESSENCIAL

        try:
            coins = await self.get_coins(interaction.user.id)

            if aposta <= 0:
                return await interaction.followup.send("Aposta inválida.")

            if aposta > coins:
                return await interaction.followup.send("Você não tem coins suficientes.")

            player, dealer = services.CardGame.start_game()

            view = views.BlackjackView(player, dealer, interaction.user.id, aposta)

            await interaction.followup.send(
                embed=view.build_embed(),
                view=view
            )

        except Exception as e:
            print("ERRO BLACKJACK:", e)
            await interaction.followup.send("Erro interno.")

#-------------SETUP---------------
async def setup(bot):
    await bot.add_cog(Casino(bot))
