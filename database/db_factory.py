from database.db_client import DBClient
from database.postgres import PostgresClient


class DBFactory:
    @staticmethod
    def create_client(db_type: str, config: dict) -> DBClient:
        if db_type == "postgres":
            return PostgresClient(config)
        raise ValueError(f"Unsupported DB type: {db_type}")