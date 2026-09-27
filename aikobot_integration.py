import asyncio
import os
import aiohttp

MONITOR_URL = os.getenv("MONITOR_URL")
MONITOR_TOKEN = os.getenv("MONITOR_TOKEN")


async def heartbeat():
    if not MONITOR_URL or not MONITOR_TOKEN:
        print("[AikoMonitor] MONITOR_URL/MONITOR_TOKEN não configurados.")
        return

    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        while True:
            try:
                async with session.post(
                    MONITOR_URL,
                    headers={"Authorization": f"Bearer {MONITOR_TOKEN}"},
                ) as response:
                    if response.status != 200:
                        print(f"[AikoMonitor] heartbeat HTTP {response.status}")
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                print(f"[AikoMonitor] falha no heartbeat: {exc}")
            await asyncio.sleep(30)
