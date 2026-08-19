import time
import hashlib
import logging
from collections import OrderedDict
import json

logger = logging.getLogger(__name__)

class TTLCache:
    def __init__(self, ttl: int = 3600, max_size: int = 100):
        self.ttl = ttl
        self.max_size = max_size
        self._cache = OrderedDict()

    def _generate_key(self, text: str, params: dict) -> str:
        data = {"text": text, "params": params}
        return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

    def get(self, text: str, params: dict) -> str | None:
        key = self._generate_key(text, params)
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl:
                logger.info(f"Cache hit for key {key[:8]}...")
                # move to end (LRU)
                self._cache.move_to_end(key)
                return value
            else:
                logger.info(f"Cache expired for key {key[:8]}...")
                del self._cache[key]
        logger.info(f"Cache miss for key {key[:8]}...")
        return None

    def set(self, text: str, params: dict, value: str):
        key = self._generate_key(text, params)
        self._cache[key] = (value, time.time())
        self._cache.move_to_end(key)
        if len(self._cache) > self.max_size:
            oldest = next(iter(self._cache))
            logger.info(f"Cache evicting oldest key {oldest[:8]}...")
            del self._cache[oldest]
        logger.info(f"Cache set for key {key[:8]}...")