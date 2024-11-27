from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .settings import get_settings

settings = get_settings()
engine = create_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_schema():
    metadata = MetaData()
    metadata.reflect(bind=engine)
    schema = {}
    for table in metadata.tables.values():
        schema[table.name] = {column.name: str(column.type) for column in table.columns}
    return schema


def query():
    pass
