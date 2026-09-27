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
                    headers={
                        "Authorization": f"Bearer {MONITOR_TOKEN}"
                    },
                ) as response:

                    body = await response.text()

                    if response.status != 200:
                        print(
                            f"[AikoMonitor] heartbeat HTTP "
                            f"{response.status}: {body}"
                        )
                    else:
                        print("[AikoMonitor] heartbeat enviado com sucesso.")

            except asyncio.CancelledError:
                raise

            except aiohttp.ClientError as exc:
                print(
                    f"[AikoMonitor] erro HTTP ao enviar heartbeat: "
                    f"{type(exc).__name__}: {exc}"
                )

            except Exception as exc:
                print(
                    f"[AikoMonitor] erro inesperado: "
                    f"{type(exc).__name__}: {exc}"
                )

            await asyncio.sleep(30)