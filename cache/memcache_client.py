from typing import Any, Optional
import memcache
from cache_client import CacheClient


class MemcacheCacheClient(CacheClient):
    def __init__(self, servers=['127.0.0.1:11211']):
        self._client = memcache.Client(servers)

    def get(self, key: str) -> Any:
        return self._client.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        self._client.set(key, value, time=ttl or 0)

    def delete(self, key: str) -> None:
        self._client.delete(key)

    def close(self) -> None:
        # memcache client has no close method
        pass
