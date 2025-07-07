# redis_client.py
from typing import Optional, Any
import redis
from cache_client import CacheClient


class RedisCacheClient(CacheClient):
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self._client = redis.Redis(host=host, port=port, db=db, password=password)

    def get(self, key: str) -> Any:
        return self._client.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._client.set(name=key, value=value, ex=ttl)

    def delete(self, key: str) -> None:
        self._client.delete(key)

    def close(self) -> None:
        self._client.close()
