from abc import ABC, abstractmethod
from platforms import PlatformGameInterface


class NotifierInterface(ABC):
    @abstractmethod
    async def fire(self, platform_game: PlatformGameInterface):
        pass
