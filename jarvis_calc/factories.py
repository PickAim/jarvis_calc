from enum import Enum
from functools import lru_cache

from jorm.market.infrastructure import Warehouse, HandlerType, Address
from jorm.market.person import Client, Account
from jorm.market.service import Request

from jarvis_calc.database_interactors import DBController


class FactoryKeywords(Enum):
    DEFAULT_WAREHOUSE = "DEFAULT_WAREHOUSE"


class JORMFactory:
    def __init__(self):
        self.__db_controller: DBController = DBController()

    @staticmethod
    def create_new_client() -> Client:
        return Client()

    @staticmethod
    def create_account(login: str, hashed_password: str, phone_number: str = "") -> Account:
        return Account(login, hashed_password, phone_number)

    @lru_cache(maxsize=5)
    def warehouse(self, warehouse_name: str) -> Warehouse:
        if warehouse_name == FactoryKeywords.DEFAULT_WAREHOUSE:
            return self.create_default_warehouse()
        return self.__db_controller.get_warehouse(warehouse_name)

    def create_default_warehouse(self) -> Warehouse:
        warehouses: list[Warehouse] = self.__db_controller.get_all_warehouses()
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
