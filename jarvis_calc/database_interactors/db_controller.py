from jorm.jarvis.db_access import UserInfoCollector, JORMCollector
from jorm.jarvis.db_update import UserInfoChanger, JORMChanger
from jorm.market.infrastructure import Warehouse, Niche, Category, Marketplace
from jorm.market.items import Product
from jorm.market.person import Account, User
from jorm.market.service import UnitEconomyRequest, UnitEconomyResult, FrequencyResult, FrequencyRequest, RequestInfo
from jorm.server.token.types import TokenType


class DBController:
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

    def update_session_tokens(self, user_id: int, old_update_token: str,
                              new_access_token: str, new_update_token: str) -> None:
        self.__user_info_changer.update_session_tokens(user_id, old_update_token, new_access_token, new_update_token)

    def update_session_tokens_by_imprint(self, access_token: str, update_token: str, imprint_token: str,
                                         user_id: int) -> None:
        self.__user_info_changer.update_session_tokens_by_imprint(access_token, update_token, imprint_token, user_id)

    def save_unit_economy_request(self, request: UnitEconomyRequest, result: UnitEconomyResult,
                                  request_info: RequestInfo, user_id: int) -> int:
        return self.__jorm_changer.save_unit_economy_request(request, result, request_info, user_id)

    def save_frequency_request(self, request: FrequencyRequest, result: FrequencyResult,
                               request_info: RequestInfo, user_id: int) -> int:
        return self.__jorm_changer.save_frequency_request(request, result, request_info, user_id)

    def save_all_tokens(self, access_token: str, update_token: str, imprint_token: str, user_id: int) -> None:
        self.__user_info_changer.save_all_tokens(access_token, update_token, imprint_token, user_id)

    def save_user_and_account(self, user: User, account: Account) -> None:
        self.__user_info_changer.save_user_and_account(user, account)

    def load_new_niche(self, niche_name: str) -> Niche:
        return self.__jorm_changer.load_new_niche(niche_name)

    def load_user_products(self, user_id: int, marketplace_id: int) -> list[Product]:
        return self.__jorm_changer.load_user_products(user_id, marketplace_id)

    def load_user_warehouse(self, user_id: int, marketplace_id: int) -> list[Product]:
        return self.__jorm_changer.load_user_warehouse(user_id, marketplace_id)

    def get_user_by_account(self, account: Account) -> User:
        return self.__user_info_collector.get_user_by_account(account)

    def get_user_by_id(self, user_id: int) -> User:
        return self.__user_info_collector.get_user_by_id(user_id)

    def get_account(self, email: str, phone: str) -> Account | None:
        account_and_id = self.__user_info_collector.get_account_and_id(email, phone)
        if account_and_id is not None:
            return account_and_id[0]
        return None

    def get_niche(self, niche_name: str, category_name: str, marketplace_id: int) -> Niche:
        return self.__jorm_collector.get_niche(niche_name, category_name, marketplace_id)

    def get_all_marketplaces(self) -> dict[int, Marketplace]:
        return self.__jorm_collector.get_all_marketplaces()

    def get_all_categories(self, marketplace_id: int) -> dict[int, Category]:
        return self.__jorm_collector.get_all_categories(marketplace_id)

    def get_warehouse(self, warehouse_name: str, marketplace_id: int) -> Warehouse:
        return self.__jorm_collector.get_warehouse(warehouse_name, marketplace_id)

    def get_all_warehouses(self, marketplace_id: int) -> list[Warehouse]:
        return self.__jorm_collector.get_all_warehouses(marketplace_id)

    def get_all_unit_economy_results(self, user_id: int) \
            -> list[tuple[UnitEconomyRequest, UnitEconomyResult, RequestInfo]]:
        return self.__jorm_collector.get_all_unit_economy_results(user_id)

    def get_all_frequency_results(self, user_id: int) \
            -> list[tuple[FrequencyRequest, FrequencyResult, RequestInfo]]:
        return self.__jorm_collector.get_all_frequency_results(user_id)

    def get_products_by_user(self, user_id: int) -> list[Product]:
        return self.__jorm_collector.get_products_by_user(user_id)

    def get_users_warehouses(self, user_id: int, marketplace_id: int) -> list[Warehouse]:
        return self.__jorm_collector.get_users_warehouses(user_id, marketplace_id)

    def delete_tokens_for_user(self, user_id: int, imprint_token: str):
        self.__user_info_changer.delete_tokens_for_user(user_id, imprint_token)

    def delete_unit_economy_request_for_user(self, request_id: int, user_id: int) -> None:
        self.__jorm_changer.delete_unit_economy_request(request_id, user_id)

    def delete_frequency_request_for_user(self, request_id: int, user_id: int) -> None:
        self.__jorm_changer.delete_frequency_request(request_id, user_id)
