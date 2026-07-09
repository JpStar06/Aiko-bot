import asyncpg
from database import get_connection

# ---------- CREATE ----------
async def criarticket(guild_id: int, channel_id: int):
    pool = get_connection()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            INSERT INTO tickets (
                guild_id, titulo, descricao, cor, emoji, canal_id,
                titulo_cliente, descricao_cliente, cor_cliente
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
            RETURNING id
            """,
            guild_id,
            "Suporte",
            "Clique no botão abaixo para abrir um ticket.",
            0x3498DB,
            "🎫",
            channel_id,
            "ESPERE SER ATENDIDO",
            "Nossa equipe pode estar ocupada.",
            0xFF0000,
        )
    return row["id"]

async def listarticket(guild_id: int):
    pool = get_connection()

    async with pool.acquire() as conn:
        tickets = await conn.fetch(
            "SELECT id, titulo FROM tickets WHERE guild_id=$1",
            guild_id
        )

    return tickets

async def get_ticket(guild_id: int, ticket_id: int):
    pool = get_connection()

    async with pool.acquire() as conn:
        ticket = await conn.fetchrow(
            "SELECT * FROM tickets WHERE guild_id=$1 AND id=$2",
            guild_id,
            ticket_id
        )

    return ticket