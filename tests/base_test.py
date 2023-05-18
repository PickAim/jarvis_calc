import math
import unittest
from datetime import datetime

from jorm.market.infrastructure import Niche, HandlerType
from jorm.market.items import Product, ProductHistory, ProductHistoryUnit
from jorm.support.types import SpecifiedLeftover, StorageDict, SpecifiedTopPlaceDict

from tests.data_for_tests import cost_data


class BaseCalcTest(unittest.TestCase):
    @staticmethod
    def create_test_product_history() -> ProductHistory:
        storage_dict = StorageDict()
        storage_dict[123] = [SpecifiedLeftover('s', 15), SpecifiedLeftover('l', 25), SpecifiedLeftover('p', 35)]
        storage_dict[321] = [SpecifiedLeftover('s', 15), SpecifiedLeftover('l', 25), SpecifiedLeftover('p', 35)]

        after_trade_storage_dict = StorageDict()
        after_trade_storage_dict[123] = [SpecifiedLeftover('l', 20), SpecifiedLeftover('p', 35)]
        after_trade_storage_dict[321] = [SpecifiedLeftover('l', 25), SpecifiedLeftover('p', 30)]

        return ProductHistory([ProductHistoryUnit(1, datetime(2021, 1, 1), storage_dict),
                               ProductHistoryUnit(3, datetime.utcnow(), storage_dict),
                               ProductHistoryUnit(5, datetime.utcnow(), after_trade_storage_dict)])

    def create_test_niche(self) -> Niche:
        niche_commissions_dict: dict[HandlerType, float] = {
            HandlerType.MARKETPLACE: 0.17,
            HandlerType.PARTIAL_CLIENT: 0.15,
            HandlerType.CLIENT: 0.10
        }
        niche_cost_data = cost_data.copy()
        niche_cost_data.sort()
        products = []
        niche_name = "Test niche"
        for i, cost in enumerate(cost_data):
            spec_leftovers: list[SpecifiedLeftover] = [SpecifiedLeftover("second", self.leftover_func(cost))]
            before_trade_storage_dict = StorageDict()
            before_trade_storage_dict[1] = spec_leftovers
            products.append(Product(f'prod{i}', cost, i, 4.0, "brand", "seller", niche_name, "default_category",
                                    history=ProductHistory([
                                        ProductHistoryUnit(1, datetime.utcnow(), before_trade_storage_dict),
                                        ProductHistoryUnit(3, datetime.utcnow(), StorageDict())]),
                                    width=0.15, height=0.3, depth=0.1,
                                    top_places=SpecifiedTopPlaceDict({'Test niche': i})))
        return Niche(niche_name, niche_commissions_dict, 0.1, products)

    @staticmethod
    def leftover_func(x) -> int:
        return int(- math.sin((x + 300_000) * 0.00001 - math.pi / 30) / (x + 200_000) * 7_500_000)


if __name__ == '__main__':
    unittest.main()
