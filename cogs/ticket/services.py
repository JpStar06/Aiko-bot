"""
Camada de acesso a dados da área de tickets.

Mantém toda a interação com o banco isolada dos cogs/views, para que
a lógica de Discord não precise conhecer SQL e vice-versa.
"""

from database import get_connection


# ---------- CREATE ----------
async def criarticket(guild_id: int, channel_id: int) -> int:
    """Cria um novo ticket com valores padrão e devolve o id gerado."""
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
    """Lista (id, titulo) de todos os tickets configurados no servidor."""
    pool = get_connection()

    async with pool.acquire() as conn:
        tickets = await conn.fetch(
            "SELECT id, titulo FROM tickets WHERE guild_id=$1",
            guild_id
        )

    return tickets


# ---------- GET ----------
async def buscar_ticket(guild_id: int, ticket_id: int):
    """Busca a configuração completa de um ticket (embed do painel + embed do cliente)."""
    pool = get_connection()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT titulo, descricao, cor, imagem, staff_id,
                   titulo_cliente, descricao_cliente, cor_cliente, imagem_cliente
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
            "staff_id": row["staff_id"],
            "title_cliente": row["titulo_cliente"],
            "description_cliente": row["descricao_cliente"],
            "color_cliente": row["cor_cliente"],
            "image_cliente": row["imagem_cliente"],
        }


# ---------- UPDATE ----------
async def editar_ticket(
    guild_id: int,
    ticket_id: int,
    novo_titulo=None,
    nova_descricao=None,
    nova_cor=None,
    imagem_url=None,
    staff_id=None,
    novo_titulo_cliente=None,
    nova_descricao_cliente=None,
    nova_cor_cliente=None,
    imagem_cliente_url=None,
):
    """Atualiza os campos informados de um ticket (painel e/ou embed do cliente).

    Campos não informados (None) mantêm o valor atual — exceto ``staff_id``,
    ``imagem_url`` e ``imagem_cliente_url``, que podem ser explicitamente
    limpos passando ``None`` só é possível recriando o ticket; aqui um valor
    ausente sempre preserva o que já estava salvo.
    """
    pool = get_connection()

    async with pool.acquire() as conn:
        data = await conn.fetchrow(
            """
            SELECT titulo, descricao, cor, imagem, staff_id,
                   titulo_cliente, descricao_cliente, cor_cliente, imagem_cliente
            FROM tickets
            WHERE id=$1 AND guild_id=$2
            """,
            ticket_id, guild_id
        )

        if not data:
            return None

        titulo = novo_titulo if novo_titulo is not None else data["titulo"]
        descricao = nova_descricao if nova_descricao is not None else data["descricao"]
        cor = nova_cor if nova_cor is not None else data["cor"]
        imagem = imagem_url if imagem_url is not None else data["imagem"]
        staff = staff_id if staff_id is not None else data["staff_id"]

        titulo_cliente = novo_titulo_cliente if novo_titulo_cliente is not None else data["titulo_cliente"]
        descricao_cliente = nova_descricao_cliente if nova_descricao_cliente is not None else data["descricao_cliente"]
        cor_cliente = nova_cor_cliente if nova_cor_cliente is not None else data["cor_cliente"]
        imagem_cliente = imagem_cliente_url if imagem_cliente_url is not None else data["imagem_cliente"]

        await conn.execute(
            """
            UPDATE tickets
            SET titulo=$1, descricao=$2, cor=$3, imagem=$4, staff_id=$5,
                titulo_cliente=$6, descricao_cliente=$7, cor_cliente=$8, imagem_cliente=$9
            WHERE id=$10 AND guild_id=$11
            """,
            titulo, descricao, cor, imagem, staff,
            titulo_cliente, descricao_cliente, cor_cliente, imagem_cliente,
            ticket_id, guild_id
        )

        return {
            "title": titulo,
            "description": descricao,
            "color": cor,
            "image": imagem,
            "staff_id": staff,
            "title_cliente": titulo_cliente,
            "description_cliente": descricao_cliente,
            "color_cliente": cor_cliente,
            "image_cliente": imagem_cliente,
        }


# ---------- PAINÉIS PERSISTENTES ----------
async def buscar_paineis():
    """Retorna todos os tickets cujo painel já foi enviado (para restaurar as views no boot)."""
    pool = get_connection()

    async with pool.acquire() as conn:
        return await conn.fetch(
            """
            SELECT id
            FROM tickets
            WHERE message_id IS NOT NULL
            """
        )


async def salvar_painel(ticket_id: int, message_id: int, channel_id: int):
    """Registra onde o painel de um ticket foi enviado, para restaurar a view após reiniciar."""
    pool = get_connection()

    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE tickets
            SET message_id=$1,
                panel_channel_id=$2
            WHERE id=$3
            """,
            message_id,
            channel_id,
            ticket_id
        )


# ---------- CANAIS DE TICKET ABERTOS ----------
async def registrar_canal_ticket(
    channel_id: int,
    ticket_id: int,
    guild_id: int,
    user_id: int,
    staff_id: int | None,
):
    """Guarda qual usuário/staff pertence a um canal de ticket recém-criado."""
    pool = get_connection()

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO ticket_channels (channel_id, ticket_id, guild_id, user_id, staff_id)
            VALUES ($1,$2,$3,$4,$5)
            ON CONFLICT (channel_id) DO NOTHING
            """,
            channel_id, ticket_id, guild_id, user_id, staff_id
        )


async def buscar_canal_ticket(channel_id: int):
    """Busca quem é o dono (e o staff responsável) de um canal de ticket."""
    pool = get_connection()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT ticket_id, guild_id, user_id, staff_id FROM ticket_channels WHERE channel_id=$1",
            channel_id
        )

    if not row:
        return None

    return dict(row)


async def usuario_tem_ticket_aberto(guild_id: int, ticket_id: int, user_id: int) -> bool:
    """Verifica se o usuário já tem um ticket aberto para este painel específico."""
    pool = get_connection()

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT channel_id FROM ticket_channels
            WHERE guild_id=$1 AND ticket_id=$2 AND user_id=$3
            """,
            guild_id, ticket_id, user_id
        )

    return row is not None


async def remover_canal_ticket(channel_id: int):
    """Remove o registro de um canal de ticket (chamado ao fechar/deletar o canal)."""
    pool = get_connection()

    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM ticket_channels WHERE channel_id=$1",
            channel_id
        )
