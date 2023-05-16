from typing import Any
from sentry_redis_tools.clients import RedisCluster

from redis.exceptions import BusyLoadingError, ConnectionError

try:
    from redis.exceptions import ClusterError
except ImportError:
    from rediscluster.exceptions import ClusterError

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
            KeyError,  # see: https://github.com/Grokzen/redis-py-cluster/issues/287
        ):
            # Codepath for redis-py-cluster
            if hasattr(self, "connection_pool"):
                self.connection_pool.nodes.reset()

            # Codepath for redis.cluster
            #
            # the code in the RedisCluster __init__ idiotically sets
            # self.nodes_manager = None
            # self.nodes_manager = NodesManager(...)
            if hasattr(self, "nodes_manager"):
                self.nodes_manager.reset()

            return super(self.__class__, self).execute_command(*args, **kwargs)
