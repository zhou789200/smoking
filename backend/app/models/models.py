from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


def _now():
    return datetime.now(timezone.utc)


class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    location = Column(String(256), nullable=False)
    zone = Column(String(128), nullable=True)
    rtsp_url = Column(String(512), nullable=True)  # RTSP stream address
    is_online = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_now)

    alerts = relationship("Alert", back_populates="camera", cascade="all, delete-orphan")


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False)
    location = Column(String(256), nullable=False)
    confidence = Column(Float, nullable=False)
    status = Column(String(16), default="active")  # active / resolved / false-positive
    detected_at = Column(DateTime, default=_now)
    resolved_at = Column(DateTime, nullable=True)
    image_path = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)

    camera = relationship("Camera", back_populates="alerts")


class Stat(Base):
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True, index=True)
    stat_date = Column(DateTime, nullable=False)
    alert_count = Column(Integer, default=0)
    resolution_rate = Column(Float, default=0.0)
    avg_response_time = Column(Float, default=0.0)  # in seconds
