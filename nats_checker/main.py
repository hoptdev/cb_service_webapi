import asyncio
import logging

from .nats_checker import start, stop

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("nats-checker-main")

async def _run(url: str):
    logger.info("Слушаем NATS (url=%s)", url)
    await start(url=url)
    logger.info("Подписались на rates.cnyrub.update")
    try:
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Останавливаем...")
        await stop()

def main():
    try:
        asyncio.run(_run("nats://nats:4222"))
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
