import discord
from discord.ext import commands
from discord import app_commands
from . import embeds


class SetupCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup", description="Configura o sistema do bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_command(self, interaction: discord.Interaction):

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild

        # 📁 procurar canal
        channel = discord.utils.get(guild.text_channels, name="aiko-painel")

        # 📁 criar se não existir
        if not channel:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=False
                )
            }

            channel = await guild.create_text_channel(
                name="aiko-painel",
                overwrites=overwrites
            )

        # 🧹 limpar mensagens antigas
        try:
            await channel.purge(limit=20)
        except:
            pass


        # 📩 enviar
        await channel.send(embed=embeds.tutorial())
        await channel.send(embed=embeds.tutorial_embed())
        await channel.send(embed=embeds.tutorial_embed2())
        await channel.send(embed=embeds.tutorial_embed3())
        await channel.send(embed=embeds.setupfinal())

        await interaction.followup.send(
            f"✅ Setup concluído em {channel.mention}",
            ephemeral=True
        )


# 🔧 loader obrigatório (NÃO MUDA)
async def setup(bot):
    await bot.add_cog(SetupCog(bot))
