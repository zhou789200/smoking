from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.schemas import AlertCreate, AlertUpdate, AlertOut, DailyStat
from app.services import alert_service

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/", response_model=list[AlertOut])
async def list_alerts(
    status: str | None = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await alert_service.get_alerts(db, status=status, limit=limit, offset=offset)


@router.get("/daily", response_model=list[DailyStat])
async def daily_stats(
    days: int = Query(7, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
):
    return await alert_service.get_daily_stats(db, days=days)


@router.get("/{alert_id}", response_model=AlertOut)
async def get_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    alert = await alert_service.get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.post("/", response_model=AlertOut, status_code=201)
async def create_alert(data: AlertCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await alert_service.create_alert(db, data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{alert_id}", response_model=AlertOut)
async def update_alert(alert_id: int, data: AlertUpdate, db: AsyncSession = Depends(get_db)):
    alert = await alert_service.update_alert(db, alert_id, data)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

