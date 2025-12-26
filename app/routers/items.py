from app.nats_client import publish as nats_publish
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db import get_db
from app.database import schemas
from app import crud
from app.websocket_manager import manager
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/", response_model=list[schemas.Item])
async def read_items(db: AsyncSession = Depends(get_db)):
    return await crud.get_items(db)

@router.get("/{item_id}", response_model=schemas.Item)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=schemas.Item)
async def create_item(item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    new_item = await crud.create_item(db, item)
    
    message = {"type": "item_created", "item": jsonable_encoder(new_item)}
    await manager.broadcast(message)
    await nats_publish("rates.cnyrub.update", message)

    return new_item

@router.patch("/{item_id}", response_model=schemas.Item)
async def update_item(item_id: int, item: schemas.ItemUpdate, db: AsyncSession = Depends(get_db)):
    updated = await crud.update_item(db, item_id, item)
    if not updated:
        raise HTTPException(status_code=404, detail="Item not found")

    message = {"type": "item_updated", "item": jsonable_encoder(updated)}
    await manager.broadcast(message)
    await nats_publish("rates.cnyrub.update", message)

    return updated

@router.delete("/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    await crud.delete_item(db, item_id)

    message = {"type": "item_deleted", "item_id": item_id}
    await manager.broadcast(message)
    await nats_publish("rates.cnyrub.update", message)

    return {"ok": True}