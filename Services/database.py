from databaseConfig import get_connection

# -------------------- USER -------------------- #
async def get_user(user_id: int) -> dict:
    pool = get_connection()

    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT coins, daily_streak, last_daily, boxes FROM economy WHERE user_id=$1",
            user_id
        )

        if not user:
            await conn.execute(
                "INSERT INTO economy (user_id, coins, daily_streak, boxes) VALUES ($1, 0, 0, 0) "
                "ON CONFLICT (user_id) DO NOTHING",
                user_id
            )
            return {"coins": 0, "daily_streak": 0, "last_daily": None, "boxes": 0}

        return dict(user)


# -------------------- COINS -------------------- #
class Coins():
    @staticmethod
    async def add(user_id: int, amount: int):
        pool = get_connection()

        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE economy SET coins = coins + $1 WHERE user_id=$2",
                amount, user_id
            )

    @staticmethod
    async def remove(user_id: int, amount: int):
        pool = get_connection()

        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE economy SET coins = coins - $1 WHERE user_id=$2",
                amount, user_id
            )
    @staticmethod
    async def get(user_id: int) -> int:
        pool = get_connection()

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT coins FROM economy WHERE user_id=$1",
                user_id
            )

            if not user:
                await conn.execute(
                    "INSERT INTO economy (user_id, coins) VALUES ($1, 0) "
                    "ON CONFLICT (user_id) DO NOTHING",
                    user_id
                )
                return 0

            return user["coins"]

class Infos():
    @staticmethod
    async def get(user_id: int) -> dict:
        pool = get_connection()

        async with pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT coins, daily_streak, last_daily, boxes FROM economy WHERE user_id=$1",
                user_id
            )

            if not user:
                await conn.execute(
                    "INSERT INTO economy (user_id, coins, daily_streak, boxes) VALUES ($1, 0, 0, 0) "
                    "ON CONFLICT (user_id) DO NOTHING",
                    user_id
                )
                return {"coins": 0, "daily_streak": 0, "last_daily": None, "boxes": 0}

            return dict(user)
