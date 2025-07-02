from typing import Dict, Any, Optional, List, Tuple
import psycopg2
from database.db_client import DBClient
from pydantic import BaseModel, Field, validator, field_validator


class DatabaseConfig(BaseModel):
    dbname: str = Field(..., min_length=1, description="Database name")
    user: str = Field(..., min_length=1, description="Database user")
    password: str = Field(..., min_length=1, description="Database password")
    host: str = Field(default="postgres_db", min_length=1)
    port: int = Field(default=5432, ge=1, le=65535)

    @field_validator('dbname', 'user', 'password', 'host')
    def non_empty(cls, v):
        if not v.strip():
            raise ValueError('Value cannot be empty or whitespace only')
        return v.strip()


class PostgresClient(DBClient):
    REQUIRED_KEYS = ["dbname", "user", "password"]

    def __init__(self, config: Dict[str, Any]):
        try:
            self.db_config = DatabaseConfig(**config)
        except Exception as e:
            raise ValueError(f"Invalid database configuration: {e}")

        self.config = config
        self.conn: Optional[psycopg2.extensions.connection] = None
        self._connect()

    def _connect(self):
        """Establish database connection"""
        if self.conn:
            self.conn.close()
        self.conn = psycopg2.connect(**self.config)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def query(self, sql: str, params: Optional[Tuple] = None) -> Optional[List[Tuple]]:
        """Execute a SELECT query and return results"""
        if not self.conn or self.conn.closed:
            self._connect()

        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, params)
                if cur.description:
                    return cur.fetchall()
                return None
        except psycopg2.Error as e:
            self.conn.rollback()
            raise

    def execute(self, sql: str, params: Optional[Tuple] = None) -> int:
        """Execute INSERT/UPDATE/DELETE and return affected rows"""
        if not self.conn or self.conn.closed:
            self._connect()

        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, params)
                self.conn.commit()
                return cur.rowcount
        except psycopg2.Error as e:
            self.conn.rollback()
            raise

    def close(self):
        """Close the DB connection and release resources"""
        if self.conn and not self.conn.closed:
            self.conn.close()