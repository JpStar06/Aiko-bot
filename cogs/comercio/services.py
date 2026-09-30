import datetime
import random

from databaseConfig import get_connection
from Services.database import Coins, Infos

PRECO_BOX = 500
VALOR_MINIMO_TRANSFERENCIA = 100  # quantia deve ser > 99

# -------------------- DAILY -------------------- #
async def daily(user_id: int) -> dict:
    pool = get_connection()
    user = await Infos.get(user_id)

    hoje = int(datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d"))

    if user["last_daily"] == hoje:
        return {"already_claimed": True}

    streak = (user["daily_streak"] or 0) + 1
    reward = random.randint(100, 500) + (streak * 20)

    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE economy SET coins=coins+$1, daily_streak=$2, last_daily=$3 WHERE user_id=$4",
            reward, streak, hoje, user_id
        )

    return {"reward": reward, "streak": streak, "already_claimed": False}


# -------------------- WORK -------------------- #
async def work(user_id: int) -> dict:
    jobs = ["programador", "minerador", "chef", "hacker", "músico"]
    job = random.choice(jobs)
    reward = random.randint(100, 400)

    await Coins.add(user_id, reward)

    return {"job": job, "reward": reward}


# -------------------- LOOTBOX -------------------- #
async def open_box(user_id: int) -> dict | None:
    pool = get_connection()

    async with pool.acquire() as conn:
        async with conn.transaction():
            user = await conn.fetchrow(
                "SELECT coins, boxes FROM economy WHERE user_id=$1 FOR UPDATE",
                user_id
            )

            if not user or user["boxes"] <= 0:
                return None

            await conn.execute(
                "UPDATE economy SET boxes = boxes - 1 WHERE user_id=$1",
                user_id
            )

            rewards = [
                (random.randint(400, 500), "🪙 comum"),
                (random.randint(500, 700), "✨ raro"),
                (random.randint(700, 900), "💎 épico"),
                (random.randint(1000, 3000), "👑 lendário"),
                (user["coins"] * 2, "🌟 mítico"),
            ]

            reward, rarity = random.choices(rewards, weights=[60, 25, 10, 5, 1])[0]

            await conn.execute(
                "UPDATE economy SET coins = coins + $1 WHERE user_id=$2",
                reward, user_id
            )

    return {"reward": reward, "rarity": rarity}


async def buy_box(user_id: int) -> dict:
    pool = get_connection()

    async with pool.acquire() as conn:
        async with conn.transaction():
            user = await conn.fetchrow(
                "SELECT coins FROM economy WHERE user_id=$1 FOR UPDATE",
                user_id
            )
            coins = user["coins"] if user else 0

            if coins < PRECO_BOX:
                return {"success": False, "faltante": PRECO_BOX - coins}

            await conn.execute(
                "UPDATE economy SET coins = coins - $1, boxes = boxes + 1 WHERE user_id=$2",
                PRECO_BOX, user_id
            )

    return {"success": True}


# -------------------- PAY -------------------- #
async def transfer(sender_id: int, target_id: int, amount: int) -> dict:
    if sender_id == target_id:
        return {"error": "self_transfer"}

    if amount <= 99:
        return {"error": "invalid_amount"}

    pool = get_connection()

    async with pool.acquire() as conn:
        async with conn.transaction():
            sender = await conn.fetchrow(
                "SELECT coins FROM economy WHERE user_id=$1 FOR UPDATE",
                sender_id
            )

            if not sender or amount > sender["coins"]:
                return {"error": "no_money"}

            taxa = int(amount * 0.02)
            recebido = amount - taxa

            await conn.execute(
                "UPDATE economy SET coins = coins - $1 WHERE user_id=$2",
                amount, sender_id
            )

            await conn.execute(
                "INSERT INTO economy (user_id, coins) VALUES ($1, 0) ON CONFLICT (user_id) DO NOTHING",
                target_id
            )

            await conn.execute(
                "UPDATE economy SET coins = coins + $1 WHERE user_id=$2",
                recebido, target_id
            )

    return {"enviado": amount, "recebido": recebido, "taxa": taxa, "target_id": target_id}


async def get_ranking(limit: int = 10) -> list[dict]:
    pool = get_connection()

    async with pool.acquire() as conn:
        users = await conn.fetch(
            "SELECT user_id, coins FROM economy ORDER BY coins DESC LIMIT $1",
            limit
        )

    return [dict(u) for u in users]
