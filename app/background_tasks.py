import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from .crud import create_item
from .websocket_manager import manager
from app.database.schemas import ItemCreate
from fastapi.encoders import jsonable_encoder
from app.nats_client import publish as nats_publish

CBR_JSON_URL = "https://www.cbr-xml-daily.ru/daily_json.js"
NATS_SUBJECT = "rates.cnyrub.update"

async def fetch_cny_rub_rate() -> float:
    async with httpx.AsyncClient(timeout=10) as client:
        res = await client.get(CBR_JSON_URL)
        res.raise_for_status()
        data = res.json()
        valute = data.get("Valute", {})
        cny = valute.get("CNY") or {}
        value = cny.get("Value")

        if value is None:
            raise httpx.HTTPError("В ответе нет курса CNY")
        
        return float(value)

async def generate_rate_item(db: AsyncSession) -> None:
    try:
        rate = await fetch_cny_rub_rate()
        item = await create_item(db, ItemCreate(date=datetime.now(), rate=rate))
        message = {"type": "rate_item_created_background", "item": jsonable_encoder(item)}
        await manager.broadcast(message)

        try:
            await nats_publish(NATS_SUBJECT, message)
        except Exception:
            pass
    except httpx.HTTPError:
        return