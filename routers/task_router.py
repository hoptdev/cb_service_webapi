from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.db import get_db
from app.background_tasks import generate_rate_item

# Provide /tasks/run endpoint as requested
router = APIRouter(prefix="/tasks", tags=["generator"])

@router.post("/run")
async def run_rate_generator(db: AsyncSession = Depends(get_db)):
    await generate_rate_item(db)
    return {"status": "rate background task triggered"}