from sqlalchemy.orm import Session
from src.database import get_schema
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text


class AIRepository:
    def __init__(self, db: Session):
        self.db = db
        self.db_schema = get_schema()

    def get_schema(self):
        return self.db_schema

    async def query(self, sql_query: str):
        try:
            result = self.db.execute(text(sql_query))
            self.db.commit()
            return [dict(row._mapping) for row in result.fetchall()]
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Error executing query: {e}")
            return None
