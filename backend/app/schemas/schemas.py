from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


# ── Camera ───────────────────────────────────────────────────────

class CameraBase(BaseModel):
    name: str = Field(..., max_length=64)
    location: str = Field(..., max_length=256)
    zone: Optional[str] = Field(None, max_length=128)
    rtsp_url: Optional[str] = Field(None, max_length=512)


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    zone: Optional[str] = None
    rtsp_url: Optional[str] = None
    is_online: Optional[bool] = None


class CameraOut(CameraBase):
    id: int
    is_online: bool
    alert_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class CameraTestResult(BaseModel):
    reachable: bool
    message: str
    rtsp_url: str


# ── Alert ────────────────────────────────────────────────────────

class AlertCreate(BaseModel):
    camera_id: int
    confidence: float = Field(..., ge=0.0, le=100.0)
    description: Optional[str] = None
    image_path: Optional[str] = None


class AlertUpdate(BaseModel):
    status: Optional[str] = None  # active / resolved / false-positive


class AlertOut(BaseModel):
    id: int
    camera_id: int
    location: str
    confidence: float
    status: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    image_path: Optional[str] = None

    class Config:
        from_attributes = True


# ── Stats ────────────────────────────────────────────────────────

class DailyStat(BaseModel):
    date: str
    count: int


class SystemStats(BaseModel):
    total_cameras: int
    online_cameras: int
    today_alerts: int
    today_resolved: int
    accuracy: float
    avg_response_time: float
