from cache_client import CacheClient
from redis_client import RedisCacheClient
from memcache_client import MemcacheCacheClient


class CacheFactory:
    @staticmethod
    def create_client(cache_type: str, config: dict) -> CacheClient:
        if cache_type == 'redis':
            return RedisCacheClient(**config)
        elif cache_type == 'memcached':
            return MemcacheCacheClient(**config)
        else:
            raise ValueError(f'Unsupported cache type: {cache_type}')
