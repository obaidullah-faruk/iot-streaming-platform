from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class DeviceBase(BaseModel):
    device_id: str

class DeviceCreate(DeviceBase):
    pass

class Device(DeviceBase):
    id: int
    first_seen: datetime
    last_seen: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TelemetryBase(BaseModel):
    device_id: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    vibration: Optional[float] = None
    timestamp: datetime

class Telemetry(TelemetryBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

class AlertBase(BaseModel):
    device_id: str
    rule_name: str
    description: Optional[str] = None
    timestamp: datetime

class Alert(AlertBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
