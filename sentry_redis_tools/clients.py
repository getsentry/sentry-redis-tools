from typing import NoReturn
from redis import RedisCluster

try:
    from rb import Cluster as BlasterClient
except ImportError:
    BlasterClient = NoReturn

from redis import StrictRedis

__all__ = ["BlasterClient", "RedisCluster", "StrictRedis"]
