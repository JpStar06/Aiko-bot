import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
from database import init_db
from cogs.ticket.view import TicketOpenView, CloseTicketView
from cogs.ticket import services

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True


class Bot(commands.Bot):
    async def setup_hook(self):
        # 🔹 Inicializa banco antes de tudo
        await init_db()

        # 🔹 Carrega cogs
        count = 0
        for folder in os.listdir("./cogs"):
            path = f"./cogs/{folder}"

            if os.path.isdir(path):
                try:
                    await self.load_extension(f"cogs.{folder}.cogs")
                    print(f"✅ Módulo '{folder}' carregada!")
                    count += 1
                except Exception as e:
                    print(f"❌ Erro ao carregar '{folder}': {e}")

        print(f"\n🚀 Total de Módulos: {count}")

        # 🔹 Sync global dos comandos
        try:
            synced = await self.tree.sync()
            print(f"módulos sincronizados: {len(synced)}")
        except Exception as e:
            print(f"❌ Erro ao sincronizar os módulos: {e}")


bot = Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    paineis = await services.buscar_paineis()
    for painel in paineis:
        bot.add_view(
            TicketOpenView(painel["id"])
        )

    print(f"🤖 Logado como {bot.user} (ID: {bot.user.id})")
    print("------")


async def main():
    async with bot:
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
