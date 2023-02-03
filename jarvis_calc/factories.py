from enum import Enum
from functools import lru_cache

from jarvis_db.access.accessers import ConcreteDBAccessProvider
from jorm.market.infrastructure import Niche, Warehouse, HandlerType, Address
from jorm.market.person import Client, Account
from jorm.market.service import Request

from .database_interactors.db_access import DBAccessProvider


class FactoryKeywords(Enum):
    DEFAULT_WAREHOUSE = "DEFAULT_WAREHOUSE"


class JORMFactory:
    def __init__(self):
        self.db_access_provider: DBAccessProvider = ConcreteDBAccessProvider()

    @staticmethod
    def create_new_client() -> Client:
        return Client()

    @staticmethod
    def create_account(login: str, hashed_password: str, phone_number: str = "") -> Account:
        return Account(login, hashed_password, phone_number)

    @lru_cache(maxsize=5)
    def warehouse(self, warehouse_name: str) -> Warehouse:
        if warehouse_name == FactoryKeywords.DEFAULT_WAREHOUSE:
            return self.__create_default_warehouse()
        return self.db_access_provider.get_warehouse(warehouse_name)

    def __create_default_warehouse(self) -> Warehouse:
        warehouses: list[Warehouse] = self.db_access_provider.get_all_warehouses()
        mean_basic_logistic_to_customer_commission: int = 0
        mean_additional_logistic_to_customer_commission: float = 0
        mean_logistic_from_customer_commission: int = 0
        mean_basic_storage_commission: int = 0
        mean_additional_storage_commission: float = 0
        mean_mono_palette_storage_commission: int = 0
        for warehouse in warehouses:
            mean_basic_logistic_to_customer_commission += warehouse.basic_logistic_to_customer_commission
            mean_additional_logistic_to_customer_commission += warehouse.additional_logistic_to_customer_commission
            mean_logistic_from_customer_commission += warehouse.logistic_from_customer_commission
            mean_basic_storage_commission += warehouse.basic_storage_commission
            mean_additional_storage_commission += warehouse.additional_storage_commission
            mean_mono_palette_storage_commission += warehouse.mono_palette_storage_commission
        mean_basic_logistic_to_customer_commission //= len(warehouses)
        mean_additional_logistic_to_customer_commission /= len(warehouses)
        mean_logistic_from_customer_commission //= len(warehouses)
        mean_basic_storage_commission //= len(warehouses)
        mean_additional_storage_commission /= len(warehouses)
        mean_mono_palette_storage_commission //= len(warehouses)
        result_warehouse: Warehouse = \
            Warehouse(str(FactoryKeywords.DEFAULT_WAREHOUSE), 0, HandlerType.MARKETPLACE, Address(), [],
                      basic_logistic_to_customer_commission=mean_basic_logistic_to_customer_commission,
                      additional_logistic_to_customer_commission=mean_additional_logistic_to_customer_commission,
                      logistic_from_customer_commission=mean_logistic_from_customer_commission,
                      basic_storage_commission=mean_basic_storage_commission,
                      additional_storage_commission=mean_additional_storage_commission,
                      mono_palette_storage_commission=mean_mono_palette_storage_commission)
        return result_warehouse

    def request(self, json_request) -> Request:
        pass
