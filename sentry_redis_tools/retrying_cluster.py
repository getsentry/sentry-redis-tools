from typing import Any
from redis.cluster import RedisCluster
from redis.exceptions import (
    BusyLoadingError,
    ConnectionError,
    ClusterError,
    TimeoutError,
)

__all__ = ["ClusterError", "RetryingRedisCluster"]


class RetryingRedisCluster(RedisCluster):  # type: ignore
    """
    Execute a command with cluster reinitialization retry logic.

    Should a cluster respond with a ConnectionError or BusyLoadingError the
    cluster nodes list will be reinitialized and the command will be executed
    again with the most up to date view of the world.
    """

    def execute_command(self, *args: Any, **kwargs: Any) -> Any:
        try:
            return super(self.__class__, self).execute_command(*args, **kwargs)
        except (
            ConnectionError,
            BusyLoadingError,
            ClusterError,
            TimeoutError,
            KeyError,  # see: https://github.com/Grokzen/redis-py-cluster/issues/287
        ):
            # the code in the RedisCluster __init__ idiotically sets
            # self.nodes_manager = None
            # self.nodes_manager = NodesManager(...)
            if hasattr(self, "nodes_manager"):
                self.nodes_manager.reset()

            return super(self.__class__, self).execute_command(*args, **kwargs)
