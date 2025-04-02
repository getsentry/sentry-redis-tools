from typing import Union, Type

import pytest
import redis

from sentry_redis_tools.clients import StrictRedis, BlasterClient, RedisCluster


def initialize_redis_cluster(cls: Type[RedisCluster] = RedisCluster) -> RedisCluster:
    if redis.VERSION >= (4,):
        client = cls.from_url("redis://127.0.0.1:16379")
    else:
        client = cls(startup_nodes=[{"host": "127.0.0.1", "port": "16379"}])

    client.flushdb()
    return client


def _build_client(param: str) -> Union[StrictRedis, RedisCluster, BlasterClient]:
    if param == "rb":
        StrictRedis().flushdb()
        return BlasterClient(hosts={0: {"port": 6379}})

    elif param == "single":
        client = StrictRedis()
        client.flushdb()
        return client

    elif param == "cluster":
        return initialize_redis_cluster()
    else:
        raise ValueError(param)


@pytest.fixture(params=["single", "cluster"])
def redis_cluster_client(
    request: pytest.FixtureRequest,
) -> Union[StrictRedis, RedisCluster]:
    rv = _build_client(request.param)
    assert not isinstance(rv, BlasterClient)
    return rv


@pytest.fixture(params=["single", "cluster", "rb"])
def redis_cluster_or_blaster_client(
    request: pytest.FixtureRequest,
) -> Union[StrictRedis, RedisCluster, BlasterClient]:
    return _build_client(request.param)
