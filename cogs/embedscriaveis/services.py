from databaseConfig import get_connection

async def criarembed(guild_id: int):
    pool = get_connection()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("""
            INSERT INTO embeds (guild_id, title, description, color, image)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """, guild_id, "Título do Embed", "Descrição padrão", 0x3498db, None)

        return row["id"]
    
async def editar_embed(guild_id: int, embed_id: int, novo_titulo=None, nova_descricao=None, nova_cor=None, imagem_url=None):
    pool = get_connection()

    async with pool.acquire() as conn:
        embed_data = await conn.fetchrow(
            "SELECT title, description, color, image FROM embeds WHERE id=$1 AND guild_id=$2",
            embed_id, guild_id
        )

        if not embed_data:
            return None

        title = novo_titulo or embed_data["title"]
        description = nova_descricao or embed_data["description"]
        color = nova_cor or embed_data["color"]
        image = imagem_url or embed_data["image"]

        await conn.execute("""
            UPDATE embeds
            SET title=$1, description=$2, color=$3, image=$4
            WHERE id=$5 AND guild_id=$6
        """, title, description, color, image, embed_id, guild_id)

        return {
            "title": title,
            "description": description,
            "color": color,
            "image": image
        }
    
async def listarembeds(guild_id: int):
    pool = get_connection()

    async with pool.acquire() as conn:
        embeds = await conn.fetch("SELECT id, title FROM embeds WHERE guild_id=$1", guild_id)

    return embeds

async def deletar_embed(guild_id: int, embed_id: int):
    pool = get_connection()

    async with pool.acquire() as conn:
        result = await conn.execute("DELETE FROM embeds WHERE id=$1 AND guild_id=$2", embed_id, guild_id)

        # result vem tipo: "DELETE 1" ou "DELETE 0"
        return result.endswith("1")
    
async def buscar_embed(guild_id: int, embed_id: int):
    pool = get_connection()

    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT title, description, color, image FROM embeds WHERE id=$1 AND guild_id=$2", embed_id, guild_id)

        if not row:
            return None

        return dict(row)