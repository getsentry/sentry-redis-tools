import pytest

from typing import Type
from unittest import mock

from redis.exceptions import BusyLoadingError, ConnectionError
from sentry_redis_tools.retrying_cluster import ClusterError, RetryingRedisCluster

from tests.conftest import initialize_redis_cluster


@pytest.mark.parametrize(
    "exception_cls",
    [
        ConnectionError,
        BusyLoadingError,
        ClusterError,
        KeyError,
    ],
)
@mock.patch("sentry_redis_tools.clients.RedisCluster.execute_command")
def test_basic(execute_command: mock.Mock, exception_cls: Type[Exception]) -> None:
    client = initialize_redis_cluster(cls=RetryingRedisCluster)

    execute_command.side_effect = exception_cls()
    execute_command.reset_mock()

    with pytest.raises(exception_cls):
        client.get("key")

    assert execute_command.call_args_list == [
        mock.call("GET", "key"),
        mock.call("GET", "key"),
    ]

    execute_command.side_effect = [exception_cls(), None]

    assert client.get("key") is None

    assert execute_command.call_args_list == [
        mock.call("GET", "key"),
        mock.call("GET", "key"),
        mock.call("GET", "key"),
        mock.call("GET", "key"),
    ]
