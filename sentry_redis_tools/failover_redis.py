import random
import time
from typing import Any

from sentry_redis_tools.clients import StrictRedis
from redis.exceptions import (
    ConnectionError,
    ReadOnlyError,
    TimeoutError,
)


class FailoverRedis(StrictRedis):  # type: ignore
    """
    Single host redis client implementation with retry logic intended to
    survive failover events. Retry logic uses capped exponential backoff with
    jitter.

    https://redis.io/commands/failover

    Failover sequence:

    1. The primary will internally start a CLIENT PAUSE WRITE, which will pause
    incoming writes and prevent the accumulation of new data in the replication
    stream. From this point all writes to the primary instance fails with
    ReadOnlyError.

    2. The primary will monitor its replicas, waiting for a replica to indicate
    that it has fully consumed the replication stream. If the primary has
    multiple replicas, it will only wait for the first replica to catch up.

    3. The primary will then demote itself to a replica. This is done to
    prevent any dual master scenarios.

    4. The previous primary will send a special PSYNC request to the target
    replica, PSYNC FAILOVER, instructing the target replica to become a
    primary.

    5. Once the previous primary receives acknowledgement the PSYNC FAILOVER
    was accepted it will unpause its clients.

    In addition, the Memorystore for Redis, which is the main target of this implementation states:

    When the primary node fails over to the replica, existing connections to
    the primary endpoint of the instance are dropped. The instance is
    unavailable for a few seconds while the new primary reconnects. On
    reconnect, your application is automatically redirected to the new primary
    node using the same connection string or IP address. You do not need to
    update your application after a failover.

    https://cloud.google.com/memorystore/docs/redis/high-availability#how_a_failover_affects_your_application

    """

    def __init__(
        self,
        *args: Any,
        _retries: int = 10,
        _backoff_min: float = 0.2,
        _backoff_max: float = 5,
        _backoff_multiplier: float = 2,
        **kwargs: Any,
    ):
        if _retries < 0:
            raise ValueError(
                f"Number of retries must non negative integer: _retries={_retries}"
            )
        self._retries = _retries

        if _backoff_min < 0.0:
            raise ValueError(
                f"Minimal backoff must be non negative number: _backoff_min={_backoff_min}"
            )
        self._backoff_min = _backoff_min

        if _backoff_max < _backoff_min:
            raise ValueError(
                f"Maximal backoff must be at least equal to the minimal ({_backoff_min}): _backoff_max={_backoff_max}"
            )
        self._backoff_max = _backoff_max

        if _backoff_multiplier <= 0:
            raise ValueError(
                f"Backoff multiplier must be positive number: _backoff_multiplier={_backoff_multiplier}"
            )
        self._backoff_multiplier = _backoff_multiplier
        super().__init__(*args, **kwargs)

    def execute_command(self, *args: Any, **kwargs: Any) -> Any:
        retries = 0
        while True:
            try:
                return super().execute_command(*args, **kwargs)
            except (
                # Caught during the inital phase of failver when writes are
                # paused on primary
                ReadOnlyError,
                # When the connection to primary is dropped and the one to the
                # replica is not ready yet.
                # ConnectionError with the errno ETIMEDOUT = 110
                ConnectionError,
                # When the client is initiated with socket_timeout or
                # socket_connect_timeout, during the reconnect it throws
                # redis.exceptions.TimeoutError instead of ConnectionError
                TimeoutError,
            ):
                if retries >= self._retries:
                    raise
                time.sleep(
                    min(
                        self._backoff_max,
                        (self._backoff_min * (self._backoff_multiplier**retries))
                        * (1 + random.random()),
                    )
                )
                retries += 1
