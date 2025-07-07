# cache_client.py
from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple


class CacheClient(ABC):
    """Unified cache client interface."""

    @abstractmethod
    def get(self, key: str) -> Any:
        ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        ...

    @abstractmethod
    def delete(self, key: str) -> None:
        ...

    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @abstractmethod
    def close(self) -> None:
        ...
