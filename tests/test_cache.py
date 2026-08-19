import time
from cachetools import TTLCach
def test_cache_hit_and_miss():
    cache = TTLCach(ttl=60, max_size=10)
    params = {"model": "test"}
    assert cache.get("text", params) is None  # miss
    cache.set("text", params, "summary")
    assert cache.get("text", params) == "summary"  # hit

def test_cache_ttl_expiration():
    cache = TTLCach(ttl=0.1, max_size=10)
    cache.set("text", {}, "summary")
    time.sleep(0.2)
    assert cache.get("text", {}) is None

def test_cache_max_size():
    cache = TTLCach(ttl=60, max_size=2)
    cache.set("1", {}, "a")
    cache.set("2", {}, "b")
    cache.set("3", {}, "c")
    assert cache.get("1", {}) is None  # вытеснена