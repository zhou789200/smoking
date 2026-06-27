from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Alert, Camera
from app.schemas.schemas import AlertCreate, AlertUpdate, AlertOut, DailyStat


async def get_alerts(
    db: AsyncSession,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[AlertOut]:
    query = select(Alert).order_by(Alert.detected_at.desc()).limit(limit).offset(offset)
    if status:
        query = query.where(Alert.status == status)
    result = await db.execute(query)
    alerts = result.scalars().all()
    return [AlertOut.model_validate(a) for a in alerts]


async def get_alert_by_id(db: AsyncSession, alert_id: int) -> AlertOut | None:
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    return AlertOut.model_validate(alert) if alert else None


async def create_alert(db: AsyncSession, data: AlertCreate) -> AlertOut:
    camera_result = await db.execute(select(Camera).where(Camera.id == data.camera_id))
    camera = camera_result.scalar_one_or_none()
    if not camera:
        raise ValueError(f"Camera {data.camera_id} not found")

    alert = Alert(
        camera_id=data.camera_id,
        location=camera.location,
        confidence=data.confidence,
        description=data.description,
        image_path=data.image_path,
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return AlertOut.model_validate(alert)


async def update_alert(db: AsyncSession, alert_id: int, data: AlertUpdate) -> AlertOut | None:
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        return None
    if data.status is not None:
        alert.status = data.status
        if data.status in ("resolved", "false-positive"):
            alert.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(alert)
    return AlertOut.model_validate(alert)


async def get_daily_stats(db: AsyncSession, days: int = 7) -> list[DailyStat]:
    from sqlalchemy import cast, Date

    query = (
        select(
            cast(Alert.detected_at, Date).label("stat_date"),
            func.count(Alert.id).label("count"),
        )
        .group_by(cast(Alert.detected_at, Date))
        .order_by(cast(Alert.detected_at, Date).desc())
        .limit(days)
    )
    result = await db.execute(query)
    rows = result.all()
    return [DailyStat(date=str(r.stat_date), count=r.count) for r in rows]
