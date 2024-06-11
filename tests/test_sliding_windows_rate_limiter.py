from typing import Union
import pytest

from sentry_redis_tools.clients import RedisCluster, StrictRedis
from sentry_redis_tools.sliding_windows_rate_limiter import (
    GrantedQuota,
    Quota,
    RedisSlidingWindowRateLimiter,
    RequestedQuota,
)


@pytest.fixture(params=["single", "cluster"])
def limiter(
    redis_cluster_client: Union[RedisCluster, StrictRedis]
) -> RedisSlidingWindowRateLimiter:
    return RedisSlidingWindowRateLimiter(redis_cluster_client)


TIMESTAMP_OFFSET = 100


def test_empty_quota(limiter: RedisSlidingWindowRateLimiter) -> None:
    quotas = [
        Quota(
            window_seconds=10,
            granularity_seconds=1,
            limit=0,
        )
    ]
    resp = limiter.check_and_use_quotas(
        [
            RequestedQuota(
                prefix="foo",
                requested=1,
                quotas=quotas,
            )
        ]
    )
    assert resp == [GrantedQuota(prefix="foo", granted=0, reached_quotas=quotas, should_throttle=False)]


def test_basic(limiter: RedisSlidingWindowRateLimiter) -> None:
    quotas = [
        Quota(
            window_seconds=10,
            granularity_seconds=1,
            limit=10,
        )
    ]

    for timestamp in range(10):
        resp = limiter.check_and_use_quotas(
            [RequestedQuota(prefix="foo", requested=1, quotas=quotas)],
            timestamp=TIMESTAMP_OFFSET + timestamp,
        )
        assert resp == [GrantedQuota(prefix="foo", granted=1, reached_quotas=[], should_throttle=False)]

    resp = limiter.check_and_use_quotas(
        [RequestedQuota(prefix="foo", requested=1, quotas=quotas)],
        timestamp=TIMESTAMP_OFFSET + 9,
    )
    assert resp == [GrantedQuota(prefix="foo", granted=0, reached_quotas=quotas, should_throttle=False)]

    for timestamp in range(10, 20):
        resp = limiter.check_and_use_quotas(
            [RequestedQuota(prefix="foo", requested=1, quotas=quotas)],
            timestamp=TIMESTAMP_OFFSET + timestamp,
        )

        assert resp == [GrantedQuota(prefix="foo", granted=1, reached_quotas=[], should_throttle=False)]

        resp = limiter.check_and_use_quotas(
            [RequestedQuota(prefix="foo", requested=1, quotas=quotas)],
            timestamp=TIMESTAMP_OFFSET + timestamp,
        )

        assert resp == [GrantedQuota(prefix="foo", granted=0, reached_quotas=quotas, should_throttle=False)]


def test_multiple_windows(limiter: RedisSlidingWindowRateLimiter) -> None:
    quotas = [
        Quota(window_seconds=10, granularity_seconds=1, limit=10),
        Quota(window_seconds=5, granularity_seconds=1, limit=5),
    ]

    resp = limiter.check_and_use_quotas(
        [RequestedQuota(prefix="foo", requested=6, quotas=quotas)],
        timestamp=TIMESTAMP_OFFSET,
    )

    assert resp == [GrantedQuota(prefix="foo", granted=5, reached_quotas=quotas[1:], should_throttle=False)]

    resp = limiter.check_and_use_quotas(
        [RequestedQuota(prefix="foo", requested=6, quotas=quotas)],
        timestamp=TIMESTAMP_OFFSET,
    )

    assert resp == [GrantedQuota(prefix="foo", granted=0, reached_quotas=quotas, should_throttle=False)]

    resp = limiter.check_and_use_quotas(
        [RequestedQuota(prefix="foo", requested=6, quotas=quotas)],
        timestamp=TIMESTAMP_OFFSET + 2,
    )

    assert resp == [GrantedQuota(prefix="foo", granted=0, reached_quotas=quotas, should_throttle=False)]

    resp = limiter.check_and_use_quotas(
        [RequestedQuota(prefix="foo", requested=6, quotas=quotas)],
        timestamp=TIMESTAMP_OFFSET + 6,
    )

    assert resp == [GrantedQuota(prefix="foo", granted=5, reached_quotas=quotas[:1], should_throttle=False)]


def test_conflicting_quotas(limiter: RedisSlidingWindowRateLimiter) -> None:
    quotas = [
        Quota(
            window_seconds=10, granularity_seconds=1, limit=10, prefix_override="hello"
        ),
    ]

    resp = limiter.check_and_use_quotas(
        [
            RequestedQuota(prefix="foo", requested=6, quotas=quotas),
            RequestedQuota(prefix="bar", requested=6, quotas=quotas),
        ],
        timestamp=TIMESTAMP_OFFSET,
    )

    assert resp == [
        GrantedQuota(prefix="foo", granted=6, reached_quotas=[], should_throttle=False),
        GrantedQuota(prefix="bar", granted=4, reached_quotas=quotas, should_throttle=False),
    ]

def test_check_within_quotas_sets_throttle(limiter: RedisSlidingWindowRateLimiter) -> None:
    quotas = [
        Quota(
            window_seconds=10,
            granularity_seconds=1,
            limit=4,
        )
    ]

    _, first_granted_quota = limiter.check_within_quotas([RequestedQuota(prefix="foo", requested=1, quotas=quotas)], TIMESTAMP_OFFSET, 2)
    assert not first_granted_quota[0].should_throttle

    _, second_granted_quota = limiter.check_within_quotas([RequestedQuota(prefix="foo", requested=1, quotas=quotas)], TIMESTAMP_OFFSET, 2)
    assert second_granted_quota[0].should_throttle
