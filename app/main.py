from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.database.db import engine, Base, SessionLocal
from app.routers import task_router
from app.websocket_manager import manager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.background_tasks import generate_rate_item
from app.routers import items as items_router
from app.nats_client import connect as nats_connect, close as nats_close

async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    scheduler = AsyncIOScheduler()

    async def job():
        async with SessionLocal() as db:
            await generate_rate_item(db)

    scheduler.add_job(job, "interval", seconds=10)

    try:
        await nats_connect()
    except Exception:
        pass

    scheduler.start()
    app.state.scheduler = scheduler

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        try:
            await nats_close()
        except Exception:
            pass

app = FastAPI(
    title="CB Service API",
    description="API для CRUD по курсу CNY→RUB и фонового парсинга, с уведомлениями через WebSocket/NATS.",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan,
)
app.include_router(task_router.router)
app.include_router(items_router.router)

@app.websocket("/ws/tasks")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)