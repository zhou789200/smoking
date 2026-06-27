import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.config import settings
from app.database import engine, async_session
from app.models.models import Base
from app.routers import cameras, alerts, stats


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed demo data if empty
    async with async_session() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM cameras"))
        count = result.scalar() or 0
        if count == 0:
            from app.models.models import Camera, Alert
            from datetime import datetime, timezone

            cameras_data = [
                Camera(name="CAM-04", location="图书馆东侧走廊", zone="图书馆", is_online=True),
                Camera(name="CAM-09", location="第三教学楼B1层", zone="教学楼B", is_online=True),
                Camera(name="CAM-11", location="宿舍楼6栋楼道", zone="宿舍区", is_online=True),
                Camera(name="CAM-15", location="操场北侧角落", zone="操场北区", is_online=False),
                Camera(name="CAM-18", location="食堂后门", zone="食堂", is_online=True),
                Camera(name="CAM-22", location="行政楼大厅", zone="行政楼", is_online=True),
            ]
            for cam in cameras_data:
                session.add(cam)
            await session.flush()  # Assign IDs before creating alerts

            alerts_data = [
                Alert(camera_id=cameras_data[0].id, location="图书馆东侧走廊", confidence=96.0, status="active",
                      detected_at=datetime(2026, 6, 27, 14, 23, tzinfo=timezone.utc)),
                Alert(camera_id=cameras_data[1].id, location="第三教学楼B1层卫生间", confidence=89.0, status="resolved",
                      detected_at=datetime(2026, 6, 27, 13, 58, tzinfo=timezone.utc)),
                Alert(camera_id=cameras_data[2].id, location="宿舍楼6栋楼道", confidence=94.0, status="resolved",
                      detected_at=datetime(2026, 6, 27, 13, 12, tzinfo=timezone.utc)),
                Alert(camera_id=cameras_data[3].id, location="操场北侧角落", confidence=61.0, status="false-positive",
                      detected_at=datetime(2026, 6, 27, 11, 45, tzinfo=timezone.utc)),
                Alert(camera_id=cameras_data[4].id, location="食堂后门", confidence=91.0, status="resolved",
                      detected_at=datetime(2026, 6, 27, 10, 30, tzinfo=timezone.utc)),
            ]
            for alert in alerts_data:
                session.add(alert)
            await session.commit()

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cameras.router)
app.include_router(alerts.router)
app.include_router(stats.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
