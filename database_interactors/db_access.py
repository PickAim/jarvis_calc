from abc import ABC, abstractmethod
from jorm.market.person import Client
from jorm.market.service import Request


class DBAccessProvider(ABC):

    @abstractmethod
    def get_client(self) -> Client:
        pass


class DBUpdateProvider(ABC):

    @abstractmethod
    def save_request(self, request: Request) -> None:
        pass
