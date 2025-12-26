import json
from typing import Optional, Any
import logging

try:
    from nats.aio.client import Client as NATS
    from nats.aio.msg import Msg
except Exception:
    NATS = None
    Msg = Any

_nc: Optional[Any] = None
_subscribed: bool = False


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("nats-checker-process")

SUBJECT = "rates.cnyrub.update"

async def _on_message(msg: Msg):
    try:
        raw = msg.data
        text = raw.decode("utf-8", errors="replace")
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = {"raw": text}

        logger.info("Получено сообщение на subject=%s: %s", msg.subject, json.dumps(payload, ensure_ascii=False))   
    except Exception:
        return

async def start(url: str = "nats://nats:4222"):
    global _nc, _subscribed
    if NATS is None:
        raise RuntimeError("nats-py is not installed")
    if _nc is None:
        nc = NATS()
        await nc.connect(servers=[url])
        _nc = nc
    if not _subscribed:
        await _nc.subscribe(SUBJECT, cb=_on_message)
        _subscribed = True

async def stop():
    global _nc, _subscribed
    try:
        if _nc is not None:
            await _nc.close()
    finally:
        _nc = None
        _subscribed = False