import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import urllib.parse

# Config
DB_USER = os.getenv('POSTGRES_USER', 'obaidullah.faruk05')
DB_PASS = urllib.parse.quote_plus(os.getenv('POSTGRES_PASSWORD', 'admin@123'))
DB_HOST = os.getenv('POSTGRES_HOST', 'postgres')
DB_PORT = os.getenv('POSTGRES_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'iot_db')

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
