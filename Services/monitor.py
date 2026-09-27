import asyncio
import os

import aiohttp


MONITOR_URL = os.getenv("MONITOR_URL")
MONITOR_TOKEN = os.getenv("MONITOR_TOKEN")


async def heartbeat():
    if not MONITOR_URL or not MONITOR_TOKEN:
        print("[Monitor] Configuração ausente.")
        return

    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as session:

        while True:
            try:
                async with session.post(
                    MONITOR_URL,
                    headers={
                        "Authorization": f"Bearer {MONITOR_TOKEN}"
                    },
                ) as response:

                    if response.status != 200:
                        print(
                            f"[Monitor] ⚠️ HTTP {response.status}"
                        )

            except asyncio.CancelledError:
                raise

            except Exception as e:
                print(
                    f"[Monitor] ❌ Falha no heartbeat: {e}"
                )

            await asyncio.sleep(30)