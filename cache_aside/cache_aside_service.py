class CacheAsideService:
    """
    Cache-aside (lazy loading) service that implements the cache-aside pattern.

    Pattern flow:
    1. Check cache first
    2. If cache miss, fetch from database
    3. Store result in cache
    4. Return result
    """

    def __init__(self, db_client: DBClient, cache_client: CacheClient,
                 default_ttl: int = 3600):
        self.db = db_client
        self.cache = cache_client
        self.default_ttl = default_ttl
        self.logger = logging.getLogger(__name__)

    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Get data using cache-aside pattern.

        Args:
            key: The key to retrieve
            ttl: Time to live in seconds (uses default if not provided)

        Returns:
            Data from cache or database, None if not found
        """
        cache_key = self._build_cache_key(key)
        ttl = ttl or self.default_ttl

        # Step 1: Try to get from cache first
        try:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                self.logger.debug(f"Cache hit for key: {key}")
                return json.loads(cached_data)
        except Exception as e:
            self.logger.warning(f"Cache read error for key {key}: {e}")
            # Continue to database if cache fails

        # Step 2: Cache miss - fetch from database
        self.logger.debug(f"Cache miss for key: {key}")
        try:
            data = self.db.get(key)
            if data is None:
                self.logger.debug(f"Data not found in database for key: {key}")
                return None

            # Step 3: Store in cache for future requests
            try:
                serialized_data = json.dumps(data)
                self.cache.set(cache_key, serialized_data, ttl)
                self.logger.debug(f"Data cached for key: {key}")
            except Exception as e:
                self.logger.warning(f"Cache write error for key {key}: {e}")
                # Return data even if caching fails

            return data

        except Exception as e:
            self.logger.error(f"Database error for key {key}: {e}")
            raise
