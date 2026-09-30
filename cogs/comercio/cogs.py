import discord
from discord import app_commands
from discord.ext import commands
from . import services
from . import embeds
from Services.database import Coins, Infos


class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    economia = app_commands.Group(name="eco", description="Sistema de economia.")
    box = app_commands.Group(name="box", description="Sistema de boxes")

    @economia.command(name="carteira", description="Mostra sua carteira")
    async def coins(self, interaction: discord.Interaction):
        user = await Infos.get(interaction.user.id)

        await interaction.response.send_message(
            embed=embeds.carteira(
                f"💰 Coins: **{user['coins']:,}**\n"
                f"📦 Boxes: **{user['boxes']:,}**\n"
                f"🔥 Daily: **{user['daily_streak']:,}**"
            )
        )

    @economia.command(name="diario", description="pegue coins diárias")
    async def daily(self, interaction: discord.Interaction):
        user = await services.daily(interaction.user.id)

        if user["already_claimed"]:
            await interaction.response.send_message(embed=embeds.erro("⏳ Você já pegou o daily hoje."))
            return

        await interaction.response.send_message(
            embed=embeds.daily(f"🎁 Daily coletado!\n+{user['reward']} coins\n🔥 Streak: {user['streak']}"))

    @economia.command(name="work", description="Trabalhe para ganhar coins.")
    @app_commands.checks.cooldown(1, 10)
    async def work(self, interaction: discord.Interaction):
        user = await services.work(interaction.user.id)

        await interaction.response.send_message(
            embed=embeds.work(f"Você trabalhou como **{user['job']}** por 1 hora\n💰 Recebeu **{user['reward']} coins**")
        )

    @work.error
    async def work_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.CommandOnCooldown):
            embed = embeds.erro(f"⏳ Espere {round(error.retry_after)} segundos para usar novamente.")
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)

    @economia.command(name="pay", description="Envie coins para outro usuário")
    async def pay(self, interaction: discord.Interaction, usuario: discord.Member, quantia: int):
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                embed=embeds.erro("❌ Você não pode pagar a si mesmo."),
                ephemeral=True
            )
            return

        data = await services.transfer(interaction.user.id, usuario.id, quantia)

        if "error" in data:
            mensagens = {
                "invalid_amount": "❌ Quantia inválida (mínimo 100 coins).",
                "no_money": "❌ Você não tem coins suficientes.",
                "self_transfer": "❌ Você não pode pagar a si mesmo.",
            }
            await interaction.response.send_message(
                embed=embeds.erro(mensagens.get(data["error"], "❌ Não foi possível concluir a transferência.")),
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=embeds.pay(
                f"💸 {interaction.user.mention} enviou **{data['recebido']} coins** para {usuario.mention}\n\n"
                f"💰 Valor: `{data['enviado']}`\n"
                f"🏦 Taxa: `{data['taxa']}`"
            )
        )

    @economia.command(name="rank", description="Ranking de coins")
    async def rank(self, interaction: discord.Interaction):
        data = await services.get_ranking()

        if not data:
            await interaction.response.send_message(embed=embeds.erro("Nenhum dado no ranking."))
            return

        text = ""
        medals = ["🥇", "🥈", "🥉"]

        for i, user in enumerate(data, start=1):
            try:
                member = interaction.guild.get_member(user["user_id"]) \
                    or await self.bot.fetch_user(user["user_id"])

                medal = medals[i - 1] if i <= 3 else f"{i}."

                text += f"{medal} {member.mention} — **{user['coins']:,} coins**\n"

            except discord.HTTPException:
                continue

        embed = discord.Embed(
            title="🏆 Ranking de Coins",
            description=text,
            color=discord.Color.gold()
        )

        await interaction.response.send_message(embed=embed)

    @box.command(name="comprar", description="Comprar lootbox")
    async def buy_box(self, interaction: discord.Interaction):
        resultado = await services.buy_box(interaction.user.id)

        if not resultado["success"]:
            await interaction.response.send_message(
                embed=embeds.erro(
                    f"Você não pode comprar essa box.\nAinda falta {resultado['faltante']} coins para finalizar a compra."
                ),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(embed=embeds.compra("📦 Você comprou uma lootbox!"))

    @box.command(name="abrir", description="Abrir lootbox")
    async def open_box(self, interaction: discord.Interaction):
        data = await services.open_box(interaction.user.id)

        if not data:
            await interaction.response.send_message(
                embed=embeds.erro("📦 Você não tem lootboxes."),
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            embed=embeds.ganhou(
                f"📦 Você abriu uma lootbox!\n"
                f"{data['rarity']}\n"
                f"💰 Você ganhou **{data['reward']} coins**"
            )
        )


async def setup(bot):
    await bot.add_cog(Economia(bot))
