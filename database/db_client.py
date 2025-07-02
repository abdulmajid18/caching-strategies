from abc import ABC, abstractmethod


class DBClient(ABC):
    @abstractmethod
    def close(self) -> None:
        """Close the database connection and release resources"""
        pass

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure connection is closed"""
        self.close()