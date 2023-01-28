from abc import ABC, abstractmethod

from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, Account
from jorm.market.service import Request


class DBAccessProvider(ABC):

    @abstractmethod
    def get_user(self, account: Account) -> User:
        pass

    @abstractmethod
    def get_account(self, login: str) -> Account:
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
    def save_request(self, request: Request, user: User) -> None:
        pass

    @abstractmethod
    def save_tokens(self, access_token: bytes, update_token: bytes, user: User) -> None:
        pass
