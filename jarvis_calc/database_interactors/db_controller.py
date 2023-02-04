from jorm.market.infrastructure import Warehouse, Niche
from jorm.market.person import Account, User
from jorm.market.service import Request

from jarvis_calc.database_interactors.db_access import DBAccessProvider, DBUpdater
from jarvis_db.access.accessers import ConcreteDBAccessProvider
from jdu.db_access.update.updaters import CalcDBUpdater


class DBController(DBUpdater, DBAccessProvider):
    __db_updater: DBUpdater = CalcDBUpdater()
    __db__accessor: DBAccessProvider = ConcreteDBAccessProvider()

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
