from jorm.market.infrastructure import Warehouse, Niche
from jorm.market.person import Account, User
from jorm.market.service import Request
from jorm.server.token.types import TokenType

from jarvis_calc.database_interactors.db_access import DBAccessProvider, DBUpdater

from jarvis_calc.database_interactors.temp_db import TempDBUpdate, TempDBAccess


class DBController:
    def __init__(self):
        self.__db_updater: DBUpdater = TempDBUpdate()
        self.__db__accessor: DBAccessProvider = TempDBAccess()

    def check_token_rnd_part(self, rnd_part_to_check: str, user_id: int, imprint: str, token_type: int) -> bool:
        if token_type == TokenType.ACCESS.value:
            rnd_part_from_db: str = self.__db__accessor.get_token_rnd_part(user_id, imprint, TokenType.ACCESS)
        elif token_type == TokenType.UPDATE.value:
            rnd_part_from_db: str = self.__db__accessor.get_token_rnd_part(user_id, imprint, TokenType.UPDATE)
        else:
            raise Exception(str(type(DBController)) + ": unexpected token type")
        return rnd_part_from_db == rnd_part_to_check

    def update_session_tokens(self, old_update_token: str, new_access_token: str, new_update_token: str) -> None:
        self.__db_updater.update_session_tokens(old_update_token, new_access_token, new_update_token)

    def update_session_tokens_by_imprint(self, access_token: str, update_token: str, imprint_token: str,
                                         user: User) -> None:
        self.__db_updater.update_session_tokens_by_imprint(access_token, update_token, imprint_token, user)

    def save_request(self, request: Request, user: User) -> None:
        self.__db_updater.save_request(request, user)

    def save_all_tokens(self, access_token: str, update_token: str, imprint_token: str, user: User) -> None:
        self.__db_updater.save_all_tokens(access_token, update_token, imprint_token, user)

    def save_user_and_account(self, user: User, account: Account) -> None:
        self.__db_updater.save_user_and_account(user, account)

    def load_new_niche(self, niche_name: str) -> Niche:
        return self.__db_updater.load_new_niche(niche_name)

    def get_user_by_account(self, account: Account) -> User:
        return self.__db__accessor.get_user_by_account(account)

    def get_user_by_id(self, user_id: int) -> User:
        return self.__db__accessor.get_user_by_id(user_id)

    def get_account(self, login: str) -> Account:
        return self.__db__accessor.get_account(login)

    def get_niche(self, niche_name: str) -> Niche:
        return self.__db__accessor.get_niche(niche_name)

    def get_warehouse(self, warehouse_name: str) -> Warehouse:
        return self.__db__accessor.get_warehouse(warehouse_name)

    def get_all_warehouses(self) -> list[Warehouse]:
        return self.__db__accessor.get_all_warehouses()
