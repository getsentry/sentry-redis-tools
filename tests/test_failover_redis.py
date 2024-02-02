import pytest

from redis.exceptions import ConnectionError, ReadOnlyError, TimeoutError

from sentry_redis_tools.failover_redis import FailoverRedis

from unittest import mock


@mock.patch("redis.StrictRedis.execute_command")
@mock.patch("time.sleep")
def test_retries(time_sleep: mock.Mock, execute_command: mock.Mock) -> None:
    client = FailoverRedis(_retries=5)
    assert client._retries == 5
    execute_command.side_effect = ConnectionError()
    with pytest.raises(ConnectionError):
        client.get("key")
    assert time_sleep.call_count == 5


@mock.patch("redis.StrictRedis.execute_command")
@mock.patch("time.sleep")
def test_recover(time_sleep: mock.Mock, execute_command: mock.Mock) -> None:
    client = FailoverRedis(_retries=5)
    assert client._retries == 5
    execute_command.side_effect = [
        ConnectionError(),
        TimeoutError(),
        ReadOnlyError(),
        "value",
    ]
    assert client.get("key") == "value"
    assert time_sleep.call_count == 3


@mock.patch("redis.StrictRedis.execute_command")
@mock.patch("time.sleep")
def test_fixed_backoff(time_sleep: mock.Mock, execute_command: mock.Mock) -> None:
    client = FailoverRedis(_backoff_max=1.0, _backoff_min=1.0)
    assert client._retries == 10
    execute_command.side_effect = ConnectionError()
    with pytest.raises(ConnectionError):
        client.get("key")
    assert time_sleep.call_args_list == 10 * [((1.0,), {})]


@mock.patch("redis.StrictRedis.execute_command")
@mock.patch("time.sleep")
def test_max_backoff(time_sleep: mock.Mock, execute_command: mock.Mock) -> None:
    client = FailoverRedis(_backoff_max=1.0, _backoff_min=0.5)
    assert client._retries == 10
    execute_command.side_effect = ConnectionError()
    with pytest.raises(ConnectionError):
        client.get("key")
    assert all(a[0][0] <= 1.0 for a in time_sleep.call_args_list)


@mock.patch("redis.client.Pipeline.execute")
@mock.patch("time.sleep")
def test_pipelines(time_sleep: mock.Mock, execute_command: mock.Mock) -> None:
    client = FailoverRedis(_backoff_max=1.0, _backoff_min=0.5)
    assert client._retries == 10
    execute_command.side_effect = ConnectionError()
    with pytest.raises(ConnectionError):
        pipe = client.pipeline()
        pipe.get("key")
        pipe.execute()  # type: ignore
    assert all(a[0][0] <= 1.0 for a in time_sleep.call_args_list)
