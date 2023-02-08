from abc import ABC, abstractmethod

from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User, Account
from jorm.market.service import Request
from jorm.server.token.types import TokenType


class DBAccessProvider(ABC):

    @abstractmethod
    def get_user_by_account(self, account: Account) -> User:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> User:
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

    @abstractmethod
    def get_token_rnd_part(self, user_id: int, imprint: str, token_type: TokenType) -> str:
        pass


class DBUpdater(ABC):
    @abstractmethod
    def update_session_tokens(self, old_update_token: str, new_access_token: str, new_update_token: str) -> None:
        # add exceptions
        pass

    @abstractmethod
    def update_session_tokens_by_imprint(self, access_token: str,
                                         update_token: str, imprint_token: str, user: User) -> None:
        pass

    @abstractmethod
    def save_request(self, request: Request, user: User) -> None:
        pass

    @abstractmethod
    def save_all_tokens(self, access_token: str, update_token: str, imprint_token: str, user: User) -> None:
        pass

    @abstractmethod
    def save_user_and_account(self, user: User, account: Account) -> None:
        pass

    @abstractmethod
    def load_new_niche(self, niche_name: str) -> Niche:
        pass
