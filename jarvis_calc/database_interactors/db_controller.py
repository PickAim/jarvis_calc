from jorm.jarvis.db_access import UserInfoCollector, JORMCollector
from jorm.jarvis.db_update import UserInfoChanger, JORMChanger
from jorm.market.infrastructure import Warehouse, Niche
from jorm.market.person import Account, User
from jorm.market.service import Request
from jorm.server.token.types import TokenType


class DBController:
    instance = None

    def __init__(self, user_info_collector: UserInfoCollector, jorm_collector: JORMCollector,
                 user_info_changer: UserInfoChanger, jorm_changer: JORMChanger):
        self.__user_info_collector: UserInfoCollector = user_info_collector
        self.__jorm_collector: JORMCollector = jorm_collector

        self.__user_info_changer: UserInfoChanger = user_info_changer
        self.__jorm_changer: JORMChanger = jorm_changer

    def check_token_rnd_part(self, rnd_part_to_check: str, user_id: int, imprint: str, token_type: int) -> bool:
        if token_type == TokenType.ACCESS.value:
            rnd_part_from_db: str = self.__user_info_collector.get_token_rnd_part(user_id, imprint, TokenType.ACCESS)
        elif token_type == TokenType.UPDATE.value:
            rnd_part_from_db: str = self.__user_info_collector.get_token_rnd_part(user_id, imprint, TokenType.UPDATE)
        else:
            raise Exception(str(type(DBController)) + ": unexpected token type")
        return rnd_part_from_db == rnd_part_to_check

    def update_session_tokens(self, old_update_token: str, new_access_token: str, new_update_token: str) -> None:
        self.__user_info_changer.update_session_tokens(old_update_token, new_access_token, new_update_token)

    def update_session_tokens_by_imprint(self, access_token: str, update_token: str, imprint_token: str,
                                         user: User) -> None:
        self.__user_info_changer.update_session_tokens_by_imprint(access_token, update_token, imprint_token, user)

    def save_request(self, request: Request, user: User) -> None:
        self.__jorm_changer.save_request(request, user)

    def save_all_tokens(self, access_token: str, update_token: str, imprint_token: str, user: User) -> None:
        self.__user_info_changer.save_all_tokens(access_token, update_token, imprint_token, user)

    def save_user_and_account(self, user: User, account: Account) -> None:
        self.__user_info_changer.save_user_and_account(user, account)

    def load_new_niche(self, niche_name: str) -> Niche:
        return self.__jorm_changer.load_new_niche(niche_name)

    def get_user_by_account(self, account: Account) -> User:
        return self.__user_info_collector.get_user_by_account(account)

    def get_user_by_id(self, user_id: int) -> User:
        return self.__user_info_collector.get_user_by_id(user_id)

    def get_account(self, email: str, phone: str) -> Account | None:
        account_and_id = self.__user_info_collector.get_account_and_id(email, phone)
        if account_and_id is not None:
            return account_and_id[0]
        return None

    def get_niche(self, niche_name: str) -> Niche:
        return self.__jorm_collector.get_niche(niche_name)

    def get_warehouse(self, warehouse_name: str) -> Warehouse:
        return self.__jorm_collector.get_warehouse(warehouse_name)

    def get_all_warehouses(self) -> list[Warehouse]:
        return self.__jorm_collector.get_all_warehouses()

    def delete_tokens_for_user(self, user: User, imprint_token: str):
        self.__user_info_changer.delete_tokens_for_user(user, imprint_token)
