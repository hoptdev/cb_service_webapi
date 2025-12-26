import json
from typing import Optional, Union, Any

try:
    from nats.aio.client import Client as NATS
except Exception:
    NATS = None

_nc: Optional[Any] = None

async def connect(url: str = "nats://nats:4222"):
    global _nc
    if NATS is None:
        raise RuntimeError("nats-py не установлен")
    nc = NATS()
    await nc.connect(servers=[url])
    _nc = nc
    return nc

async def publish(subject: str, message: Union[dict, str, bytes]) -> bool:
    if _nc is None:
        return False
    
    payload: bytes

    if isinstance(message, dict):
        payload = json.dumps(message, ensure_ascii=False).encode("utf-8")
    elif isinstance(message, str):
        payload = message.encode("utf-8")
    else:
        payload = message
    await _nc.publish(subject, payload)

    return True

async def close():
    global _nc
    if _nc is not None:
        try:
            await _nc.close()
        finally:
            _nc = None