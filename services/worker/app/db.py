import os
import logging
from database.core.database import Base, SessionLocal, engine

logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
