from abc import abstractmethod
from typing import Mapping, Optional, Protocol, Union, runtime_checkable

Tags = Mapping[str, str]


@runtime_checkable
class Metrics(Protocol):
    """
    An abstract class that defines the interface for metrics backends.
    """

    @abstractmethod
    def increment(
        self, name: str, value: Union[int, float] = 1, tags: Optional[Tags] = None
    ) -> None:
        """
        Increments a counter metric by a given value.
        """
        raise NotImplementedError

    @abstractmethod
    def gauge(
        self, name: str, value: Union[int, float], tags: Optional[Tags] = None
    ) -> None:
        """
        Sets a gauge metric to the given value.
        """
        raise NotImplementedError

    @abstractmethod
    def timing(
        self, name: str, value: Union[int, float], tags: Optional[Tags] = None
    ) -> None:
        """
        Records a timing metric.
        """
        raise NotImplementedError


class DummyMetricsBackend(Metrics):
    """
    Default metrics backend that does not record anything.
    """

    def increment(
        self, name: str, value: Union[int, float] = 1, tags: Optional[Tags] = None
    ) -> None:
        pass

    def gauge(
        self, name: str, value: Union[int, float], tags: Optional[Tags] = None
    ) -> None:
        pass

    def timing(
        self, name: str, value: Union[int, float], tags: Optional[Tags] = None
    ) -> None:
        pass
