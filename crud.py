from sqlalchemy.ext.asyncio import AsyncSession
from .database.models import RateItem
from .database.schemas import ItemCreate, ItemUpdate
from sqlalchemy import select

async def get_items(db: AsyncSession):
    result = await db.execute(select(RateItem).order_by(RateItem.date.desc()))
    return result.scalars().all()

async def get_item(db: AsyncSession, item_id: int):
    return await db.get(RateItem, item_id)

async def create_item(db: AsyncSession, item: ItemCreate):
    data = item.model_dump()
    db_item = RateItem(**data)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

async def update_item(db: AsyncSession, item_id: int, item: ItemUpdate):
    db_item = await get_item(db, item_id)
    if db_item:
        for key, value in item.model_dump(exclude_unset=True).items():
            setattr(db_item, key, value)
        await db.commit()
        await db.refresh(db_item)
    return db_item

async def delete_item(db: AsyncSession, item_id: int):
    db_item = await get_item(db, item_id)
    if db_item:
        await db.delete(db_item)
        await db.commit()
    return db_item