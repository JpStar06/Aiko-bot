"""
Camada de acesso ao banco de dados.
Ajuste o nome da tabela ("configuracoes") para o nome real usado no seu projeto.
Assume-se um pool asyncpg (PostgreSQL), coerente com os tipos vistos na imagem
(id serial, guild_id bigint, etc).
"""

import asyncpg

# Campos que podem ser atualizados a partir do editor de embeds.
# Mantemos uma whitelist para evitar montar SQL com nomes de coluna arbitrários.
CAMPOS_PERMITIDOS = {
    "titulo", "descricao", "cor", "imagem", "emoji",
    "titulo_cliente", "descricao_cliente", "cor_cliente",
    "imagem_cliente", "mensagem_cliente",
}


class Database:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_config(self, guild_id: int) -> dict | None:
        query = "SELECT * FROM configuracoes WHERE guild_id = $1"
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(query, guild_id)
            return dict(row) if row else None

    async def update_field(self, guild_id: int, field: str, value) -> None:
        if field not in CAMPOS_PERMITIDOS:
            raise ValueError(f"Campo não permitido para edição: {field}")

        query = f"UPDATE configuracoes SET {field} = $1 WHERE guild_id = $2"
        async with self.pool.acquire() as conn:
            await conn.execute(query, value, guild_id)

    async def update_many(self, guild_id: int, valores: dict) -> None:
        """Atualiza vários campos de uma vez (uma query por campo, dentro de uma transação)."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                for field, value in valores.items():
                    if field not in CAMPOS_PERMITIDOS:
                        raise ValueError(f"Campo não permitido para edição: {field}")
                    await conn.execute(
                        f"UPDATE configuracoes SET {field} = $1 WHERE guild_id = $2",
                        value, guild_id
                    )