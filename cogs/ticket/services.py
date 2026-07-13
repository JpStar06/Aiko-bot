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


# ---------- LIST ----------
async def listarticket(guild_id: int):
    pool = get_connection()

    async with pool.acquire() as conn:
        tickets = await conn.fetch(
            "SELECT id, titulo FROM tickets WHERE guild_id=$1",
            guild_id
        )

    return tickets


# ---------- GET ----------
async def buscar_ticket(guild_id: int, ticket_id: int):
    pool = get_connection()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT titulo, descricao, cor, imagem, staff_id
            FROM tickets
            WHERE id=$1 AND guild_id=$2
            """,
            ticket_id, guild_id
        )

        if not row:
            return None

        return {
            "title": row["titulo"],
            "description": row["descricao"],
            "color": row["cor"],
            "image": row["imagem"],
            "staff_id": row["staff_id"]
        }


# ---------- UPDATE ----------
async def editar_ticket(
    guild_id: int,
    ticket_id: int,
    novo_titulo=None,
    nova_descricao=None,
    nova_cor=None,
    imagem_url=None,
    staff_id=None
):
    pool = get_connection()

    async with pool.acquire() as conn:
        data = await conn.fetchrow(
            """
            SELECT titulo, descricao, cor, imagem, staff_id
            FROM tickets
            WHERE id=$1 AND guild_id=$2
            """,
            ticket_id, guild_id
        )

        if not data:
            return None

        titulo = novo_titulo or data["titulo"]
        descricao = nova_descricao or data["descricao"]
        cor = nova_cor if nova_cor is not None else data["cor"]
        imagem = imagem_url if imagem_url is not None else data["imagem"]
        staff = staff_id if staff_id is not None else data["staff_id"]

        await conn.execute(
            """
            UPDATE tickets
            SET titulo=$1, descricao=$2, cor=$3, imagem=$4, staff_id=$5
            WHERE id=$6 AND guild_id=$7
            """,
            titulo, descricao, cor, imagem, staff, ticket_id, guild_id
        )

        return {
            "title": titulo,
            "description": descricao,
            "color": cor,
            "image": imagem,
            "staff_id": staff
        }