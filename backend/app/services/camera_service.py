from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Camera, Alert
from app.schemas.schemas import CameraCreate, CameraUpdate, CameraOut


async def get_cameras(db: AsyncSession, online_only: bool | None = None) -> list[dict]:
    query = select(Camera).order_by(Camera.id)
    if online_only is not None:
        query = query.where(Camera.is_online == online_only)
    result = await db.execute(query)
    cameras = result.scalars().all()

    out = []
    for cam in cameras:
        alert_count_result = await db.execute(
            select(func.count(Alert.id)).where(
                Alert.camera_id == cam.id, Alert.status == "active"
            )
        )
        alert_count = alert_count_result.scalar() or 0
        out.append(
            {
                "id": cam.id,
                "name": cam.name,
                "location": cam.location,
                "zone": cam.zone,
                "rtsp_url": cam.rtsp_url,
                "is_online": cam.is_online,
                "alert_count": alert_count,
                "created_at": cam.created_at,
            }
        )
    return out


async def get_camera_by_id(db: AsyncSession, camera_id: int) -> CameraOut | None:
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    cam = result.scalar_one_or_none()
    if not cam:
        return None

    alert_count_result = await db.execute(
        select(func.count(Alert.id)).where(
            Alert.camera_id == cam.id, Alert.status == "active"
        )
    )
    return CameraOut(
        id=cam.id,
        name=cam.name,
        location=cam.location,
        zone=cam.zone,
        rtsp_url=cam.rtsp_url,
        is_online=cam.is_online,
        alert_count=alert_count_result.scalar() or 0,
        created_at=cam.created_at,
    )


async def create_camera(db: AsyncSession, data: CameraCreate) -> CameraOut:
    camera = Camera(**data.model_dump())
    db.add(camera)
    await db.commit()
    await db.refresh(camera)
    return CameraOut(
        id=camera.id,
        name=camera.name,
        location=camera.location,
        zone=camera.zone,
        rtsp_url=camera.rtsp_url,
        is_online=camera.is_online,
        alert_count=0,
        created_at=camera.created_at,
    )


async def update_camera(db: AsyncSession, camera_id: int, data: CameraUpdate) -> CameraOut | None:
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    cam = result.scalar_one_or_none()
    if not cam:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(cam, key, value)
    await db.commit()
    await db.refresh(cam)

    alert_count_result = await db.execute(
        select(func.count(Alert.id)).where(
            Alert.camera_id == cam.id, Alert.status == "active"
        )
    )
    return CameraOut(
        id=cam.id,
        name=cam.name,
        location=cam.location,
        zone=cam.zone,
        rtsp_url=cam.rtsp_url,
        is_online=cam.is_online,
        alert_count=alert_count_result.scalar() or 0,
        created_at=cam.created_at,
    )


async def delete_camera(db: AsyncSession, camera_id: int) -> bool:
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    cam = result.scalar_one_or_none()
    if not cam:
        return False

    # 先删除关联的告警记录（外键约束）
    await db.execute(
        delete(Alert).where(Alert.camera_id == camera_id)
    )
    await db.delete(cam)
    await db.commit()
    return True
