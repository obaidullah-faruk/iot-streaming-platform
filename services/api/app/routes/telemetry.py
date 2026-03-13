from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.session import get_db
from app.models import schemas
from database.models import schema as db_models

router = APIRouter(prefix="/telemetry", tags=["telemetry"])

@router.get("/", response_model=List[schemas.Telemetry])
def read_telemetry(
    device_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(db_models.Telemetry)
    
    if device_id:
        query = query.filter(db_models.Telemetry.device_id == device_id)
    if start_time:
        query = query.filter(db_models.Telemetry.timestamp >= start_time)
    if end_time:
        query = query.filter(db_models.Telemetry.timestamp <= end_time)
        
    telemetry_data = query.order_by(db_models.Telemetry.timestamp.desc()).offset(skip).limit(limit).all()
    return telemetry_data
