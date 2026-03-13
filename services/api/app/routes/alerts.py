from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.models import schemas
from database.models import schema as db_models

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/", response_model=List[schemas.Alert])
def read_alerts(
    device_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(db_models.Alert)
    
    if device_id:
        query = query.filter(db_models.Alert.device_id == device_id)
        
    alerts = query.order_by(db_models.Alert.timestamp.desc()).offset(skip).limit(limit).all()
    return alerts
