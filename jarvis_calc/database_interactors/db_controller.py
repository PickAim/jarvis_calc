from jorm.jarvis.db_access import UserInfoCollector, JORMCollector
from jorm.jarvis.db_update import UserInfoChanger, JORMChanger
from jorm.market.infrastructure import Warehouse, Niche, Category, Marketplace
from jorm.market.items import Product
from jorm.market.person import Account, User
from jorm.market.service import SimpleEconomySaveObject, TransitEconomySaveObject
from jorm.server.token.types import TokenType
from jorm.support.types import EconomyConstants

_DEFAULT_ECONOMY_CONSTANTS = EconomyConstants(
    max_mass=25,
    max_side_sum=200,
    max_side_length=120,
    max_standard_volume_in_liters=5,
    return_price=50_00,
    oversize_logistic_price=1000_00,
    oversize_storage_price=2_157,
    standard_warehouse_logistic_price=50_00,
    standard_warehouse_storage_price=30,
    nds_tax=0.20,
    commercial_tax=0.15,
    self_employed_tax=0.06,
)


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

    def check_token_exist(self, user_id: int, imprint: str, token_type: int) -> bool:
        if token_type == TokenType.ACCESS.value:
            rnd_part_from_db: str = self.__user_info_collector.get_token_rnd_part(user_id, imprint, TokenType.ACCESS)
        elif token_type == TokenType.UPDATE.value:
            rnd_part_from_db: str = self.__user_info_collector.get_token_rnd_part(user_id, imprint, TokenType.UPDATE)
        else:
            raise Exception(str(type(DBController)) + ": unexpected token type")
        return rnd_part_from_db is not None

    def add_marketplace_api_key(self, api_key: str, user_id: int, marketplace_id: int) -> None:
        self.__user_info_changer.add_marketplace_api_key(api_key, user_id, marketplace_id)

    def update_niche(self, niche_id: int, category_id: int, marketplace_id: int) -> Niche:
        return self.__jorm_changer.update_niche(niche_id, category_id, marketplace_id)

    def update_session_tokens(self, user_id: int, old_update_token: str,
                              new_access_token: str, new_update_token: str) -> None:
        self.__user_info_changer.update_session_tokens(user_id, old_update_token, new_access_token, new_update_token)

    def update_session_tokens_by_imprint(self, access_token: str, update_token: str, imprint_token: str,
                                         user_id: int) -> None:
        self.__user_info_changer.update_session_tokens_by_imprint(access_token, update_token, imprint_token, user_id)

    def update_economy_constants(self, marketplace_id: int, economy_constants: EconomyConstants) -> None:
        self.__jorm_changer.update_economy_constants(marketplace_id, economy_constants)

    def save_simple_economy_request(self, save_object: SimpleEconomySaveObject, user_id: int) -> int:
        return self.__jorm_changer.save_simple_economy_request(save_object, user_id)

    def save_transit_economy_request(self, save_object: TransitEconomySaveObject, user_id: int) -> int:
        return self.__jorm_changer.save_transit_economy_request(save_object, user_id)

    def save_all_tokens(self, access_token: str, update_token: str, imprint_token: str, user_id: int) -> None:
        self.__user_info_changer.save_all_tokens(access_token, update_token, imprint_token, user_id)

    def save_user_and_account(self, user: User, account: Account) -> None:
        self.__user_info_changer.save_user_and_account(user, account)

    def load_new_niche(self, niche_name: str, marketplace_id: int) -> Niche | None:
        return self.__jorm_changer.load_new_niche(niche_name, marketplace_id)

    def load_user_products(self, user_id: int, marketplace_id: int) -> list[Product]:
        return self.__jorm_changer.load_user_products(user_id, marketplace_id)

    def load_user_warehouse(self, user_id: int, marketplace_id: int) -> list[Warehouse]:
        return self.__jorm_changer.load_user_warehouses(user_id, marketplace_id)

    def get_economy_constants(self, marketplace_id: int) -> EconomyConstants:
        found = self.__jorm_collector.get_economy_constants(marketplace_id)
        if found is not None:
            return found
        return _DEFAULT_ECONOMY_CONSTANTS

    def get_user_by_account(self, account: Account) -> User:
        return self.__user_info_collector.get_user_by_account(account)

    def get_user_by_id(self, user_id: int) -> User:
        return self.__user_info_collector.get_user_by_id(user_id)

    def get_account(self, email: str, phone: str) -> Account | None:
        account_and_id = self.__user_info_collector.get_account_and_id(email, phone)
        if account_and_id is not None:
            return account_and_id[0]
        return None

    def get_niche(self, niche_name: str, category_id: int, marketplace_id: int) -> Niche | None:
        return self.__jorm_collector.get_niche(niche_name, category_id, marketplace_id)

    def get_niche_by_id(self, niche_id: int) -> Niche | None:
        return self.__jorm_collector.get_niche_by_id(niche_id)

    def get_niche_without_history(self, niche_id: int) -> Niche | None:
        return self.__jorm_collector.get_niche_without_history(niche_id)

    def get_warehouse(self, warehouse_id: int) -> Warehouse:
        return self.__jorm_collector.get_warehouse(warehouse_id)

    def get_all_marketplaces(self) -> dict[int, Marketplace]:
        return self.__jorm_collector.get_all_marketplaces()

    def get_all_categories(self, marketplace_id: int) -> dict[int, Category]:
        return self.__jorm_collector.get_all_categories(marketplace_id)

    def get_all_niches(self, category_id: int) -> dict[int, Niche]:
        return self.__jorm_collector.get_all_niches(category_id)

    def get_all_warehouses(self, marketplace_id: int) -> dict[int, Warehouse]:
        return self.__jorm_collector.get_all_warehouses(marketplace_id)

    def get_all_marketplaces_atomic(self) -> dict[int, Marketplace]:
        return self.__jorm_collector.get_all_marketplaces_atomic()

    def get_all_categories_atomic(self, marketplace_id: int) -> dict[int, Category]:
        return self.__jorm_collector.get_all_categories_atomic(marketplace_id)

    def get_all_niches_atomic(self, category_id: int) -> dict[int, Niche]:
        return self.__jorm_collector.get_all_niches_atomic(category_id)

    def get_all_warehouses_atomic(self, marketplace_id: int) -> dict[int, Warehouse]:
        return self.__jorm_collector.get_all_warehouses_atomic(marketplace_id)

    def get_all_simple_economy_results(self, user_id: int) -> list[SimpleEconomySaveObject]:
        return self.__jorm_collector.get_all_simple_economy_results(user_id)

    def get_all_transit_economy_results(self, user_id: int) -> list[TransitEconomySaveObject]:
        return self.__jorm_collector.get_all_transit_economy_results(user_id)

    def get_products_by_user(self, user_id: int, marketplace_id: int) -> dict[int, Product]:
        return self.__jorm_collector.get_products_by_user(user_id, marketplace_id)

    def get_products_by_user_atomic(self, user_id: int, marketplace_id: int) -> dict[int, Product]:
        return self.__jorm_collector.get_products_by_user_atomic(user_id, marketplace_id)

    def get_users_warehouses(self, user_id: int, marketplace_id: int) -> dict[int, Warehouse]:
        return self.__jorm_collector.get_users_warehouses(user_id, marketplace_id)

    def delete_marketplace_api_key(self, user_id: int, marketplace_id: int) -> None:
        self.__user_info_changer.delete_marketplace_api_key(user_id, marketplace_id)

    def delete_account(self, user_id: int) -> None:
        self.__user_info_changer.delete_account(user_id)

    def delete_tokens_for_user(self, user_id: int, imprint_token: str):
        self.__user_info_changer.delete_tokens_for_user(user_id, imprint_token)

    def delete_simple_economy_request(self, request_id: int, user_id: int) -> None:
        self.__jorm_changer.delete_simple_economy_request(request_id, user_id)

    def delete_transit_economy_request(self, request_id: int, user_id: int) -> None:
        self.__jorm_changer.delete_transit_economy_request(request_id, user_id)
