from abc import ABC, abstractmethod


class Pretty(ABC):
    @abstractmethod
    def __pretty__(self) -> str:
        ...
