from abc import ABC, abstractmethod

from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import Client
from jorm.market.service import Request


class DBAccessProvider(ABC):

    @abstractmethod
    def get_client(self) -> Client:
        pass

    @abstractmethod
    def get_niche(self, niche_name: str) -> Niche:
        pass

    @abstractmethod
    def get_warehouse(self, warehouse_name: str) -> Warehouse:
        pass

    @abstractmethod
    def get_all_warehouses(self) -> list[Warehouse]:
        pass


class DBUpdateProvider(ABC):

    @abstractmethod
    def save_request(self, request: Request) -> None:
        pass
