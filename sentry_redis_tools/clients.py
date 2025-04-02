from typing import NoReturn

try:
    from redis import RedisCluster
except ImportError:
    from rediscluster import RedisCluster

try:
    from rb import Cluster as BlasterClient
except ImportError:
    BlasterClient = NoReturn

from redis import StrictRedis

__all__ = ["BlasterClient", "RedisCluster", "StrictRedis"]
