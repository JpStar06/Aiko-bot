import asyncpg
import os

pool = None

# iniciar conexão com pool
async def init_db():
    global pool

    DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não encontrada no .env")

    pool = await asyncpg.create_pool(
        DATABASE_URL,
        ssl="require",
        min_size=1,
        max_size=5
    )


    # cria tabelas
    async with pool.acquire() as conn:

        # embeds
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS embeds (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,
            title TEXT,
            description TEXT,
            color INTEGER,
            image TEXT
        )
        """)

        # tickets
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,
            titulo TEXT,
            descricao TEXT,
            cor INTEGER,
            emoji TEXT,
            canal_id BIGINT,
            staff_id BIGINT,
            imagem TEXT,
            titulo_cliente TEXT,
            descricao_cliente TEXT,
            cor_cliente INTEGER,
            imagem_cliente TEXT,
            message_id BIGINT,
            panel_channel_id BIGINT
        )
        """)

        # economy
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS economy (
            user_id BIGINT PRIMARY KEY,
            coins BIGINT NOT NULL DEFAULT 0,
            last_daily BIGINT NOT NULL DEFAULT 0,
            daily_streak BIGINT NOT NULL DEFAULT 0,
            boxes BIGINT NOT NULL DEFAULT 0
        )
        """)

        # reminders
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id SERIAL PRIMARY KEY,
            guild_id BIGINT,
            channel_id BIGINT,
            embed_id INTEGER,
            horario TEXT
        )
        """)

        print("📦 Tabelas verificadas/criadas com sucesso!")


# pegar conexão do pool
def get_connection():
    global pool
    if pool is None:
        raise ValueError("Pool não inicializado. Use init_db() primeiro.")
    return pool
