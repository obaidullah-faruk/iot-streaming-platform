from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, BigInteger
from database.core.database import Base

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, nullable=False)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    device_id = Column(String, ForeignKey("devices.device_id"), index=True, nullable=False)
    temperature = Column(Float)
    humidity = Column(Float)
    vibration = Column(Float)
    timestamp = Column(DateTime(timezone=True), primary_key=True, index=True, nullable=False)
    
    __table_args__ = (
        Index('idx_telemetry_device_time', 'device_id', 'timestamp'),
    )


class Alert(Base):
    __tablename__ = "alerts"
    id = Column(BigInteger, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.device_id"), index=True, nullable=False)
    rule_name = Column(String, nullable=False)
    description = Column(String)
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
