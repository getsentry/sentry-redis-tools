from __future__ import annotations

from typing import Any, Optional, List, Dict, TypedDict

from redis.sentinel import Sentinel
from sentry_redis_tools.clients import StrictRedis


class SentinelNodes(TypedDict):
    host: str
    port: int


class SentinelCluster(StrictRedis):  # type: ignore
    """ """

    _sentinel_client: Optional[Sentinel] = None

    def __new__(
        cls,
        *args: Any,
        sentinel_nodes: Optional[List[SentinelNodes]] = None,
        service_name: Optional[str] = None,
        **kwargs: Any,
    ) -> SentinelCluster:
        if sentinel_nodes and service_name:
            sentinel = Sentinel(
                [(node["host"], node["port"]) for node in sentinel_nodes],
                **kwargs,
            )
            return sentinel.master_for(  # type: ignore
                service_name=service_name,
                redis_class=cls,
            )

        return super().__new__(cls)  # type: ignore

    def __init__(
        self,
        *args: Any,
        sentinel_nodes: Optional[List[Dict[str, Any]]] = None,
        service_name: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
