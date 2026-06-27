from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.schemas import CameraCreate, CameraUpdate, CameraOut, CameraTestResult
from app.services import camera_service
import asyncio

router = APIRouter(prefix="/api/cameras", tags=["cameras"])


async def _test_rtsp_connection(rtsp_url: str, timeout: int = 5) -> CameraTestResult:
    """Test if an RTSP stream is reachable by attempting a TCP connection."""
    import socket
    from urllib.parse import urlparse

    try:
        parsed = urlparse(rtsp_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 554

        # Try TCP connection first (quick check)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            return CameraTestResult(
                reachable=True,
                message=f"RTSP 端口 {host}:{port} 连接成功",
                rtsp_url=rtsp_url,
            )
        else:
            return CameraTestResult(
                reachable=False,
                message=f"无法连接到 {host}:{port}（错误码: {result}）",
                rtsp_url=rtsp_url,
            )
    except socket.timeout:
        return CameraTestResult(
            reachable=False,
            message=f"连接 {rtsp_url} 超时",
            rtsp_url=rtsp_url,
        )
    except Exception as e:
        return CameraTestResult(
            reachable=False,
            message=f"连接失败: {str(e)}",
            rtsp_url=rtsp_url,
        )


@router.post("/test", response_model=CameraTestResult)
async def test_camera_connection(payload: CameraCreate):
    """Test camera RTSP connection before creating the device."""
    if not payload.rtsp_url:
        raise HTTPException(status_code=400, detail="需要提供 RTSP 地址")
    return await _test_rtsp_connection(payload.rtsp_url)


@router.get("/", response_model=list[dict])
async def list_cameras(
    online_only: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    return await camera_service.get_cameras(db, online_only=online_only)


@router.get("/{camera_id}", response_model=CameraOut)
async def get_camera(camera_id: int, db: AsyncSession = Depends(get_db)):
    cam = await camera_service.get_camera_by_id(db, camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam


@router.post("/", response_model=CameraOut, status_code=201)
async def create_camera(data: CameraCreate, db: AsyncSession = Depends(get_db)):
    return await camera_service.create_camera(db, data)


@router.patch("/{camera_id}", response_model=CameraOut)
async def update_camera(camera_id: int, data: CameraUpdate, db: AsyncSession = Depends(get_db)):
    cam = await camera_service.update_camera(db, camera_id, data)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return cam


@router.delete("/{camera_id}", status_code=204)
async def delete_camera(camera_id: int, db: AsyncSession = Depends(get_db)):
    ok = await camera_service.delete_camera(db, camera_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Camera not found")
