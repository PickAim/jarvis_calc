import datetime
import math
import unittest

from jorm.market.infrastructure import Niche, Warehouse, Address, HandlerType
from jorm.market.items import ProductHistory, Product, ProductHistoryUnit
from jorm.market.person import Client, ClientInfo, ClientPrivilege
from jorm.support.types import StorageDict, ProductSpecifyDict

from jarvis_calc.utils.calculators import FrequencyCalculator, UnitEconomyCalculator
from jarvis_calc.utils.temporary import get_commission_for, get_return_percent_for
from tests.test_data import cost_data


class CalculatorsTest(unittest.TestCase):

    def test_only_freq_calc_with_jorm(self):
        calculator = FrequencyCalculator()
        niche: Niche = self.create_test_niche()
        x, y = calculator.get_frequency_stats(niche)
        self.assertEqual(int(len(cost_data) * 0.1), len(x))

    def test_mean_concurrent_cost_calc_with_niche(self):
        niche: Niche = self.create_test_niche()
        buy = 500_00
        pack = 150_00
        unit_cost: int = buy + pack
        mid_cost: int = niche.get_mean_concurrent_cost(unit_cost, 5500, 15)
        self.assertEqual(971_23, mid_cost)

    def test_unit_economy_calc_with_jorm(self):
        calculator = UnitEconomyCalculator()
        niche: Niche = self.create_test_niche()
        buy: int = 50_00
        pack: int = 50_00
        transit_price: int = 1000_00
        transit_count: int = 1000
        marketplace_transit_price: int = 1500_00
        warehouse = Warehouse("warehouse", 1, HandlerType.MARKETPLACE, Address(), [],
                              basic_logistic_to_customer_commission=55_00, additional_logistic_to_customer_commission=0,
                              logistic_from_customer_commission=33_00, basic_storage_commission=15,
                              additional_storage_commission=0, mono_palette_storage_commission=10)
        client = Client(name="client", privilege=ClientPrivilege.BASIC, client_info=ClientInfo(profit_tax=0.06))
        result = calculator.calc_unit_economy(buy, pack, niche, warehouse, client,
                                              transit_price, transit_count, marketplace_transit_price)
        self.assertEqual(69_57, result["Margin"][0])

    def test_niche_info_load(self):
        commission: float = get_commission_for("Автомобильные товары",
                                               "Подстаканники электрические", str(HandlerType.MARKETPLACE))
        self.assertEqual(0.17, commission)
        return_percent: float = get_return_percent_for("Автомобильные товары", "Подстаканники электрические")
        self.assertEqual(0.1, return_percent)

    def create_test_niche(self) -> Niche:
        niche_commissions_dict: dict[HandlerType, float] = {
            HandlerType.MARKETPLACE: 0.17,
            HandlerType.PARTIAL_CLIENT: 0.15,
            HandlerType.CLIENT: 0.10
        }
        niche_cost_data = cost_data.copy()
        niche_cost_data.sort()
        products = []

        for i, cost in enumerate(cost_data):
            product_specify_dict = ProductSpecifyDict()
            product_specify_dict['t'] = self.leftover_func(cost)
            before_trade_storage_dict = StorageDict()
            before_trade_storage_dict[1] = product_specify_dict
            products.append(Product(f'prod{i}', cost, i,
                                    history=ProductHistory([
                                        ProductHistoryUnit(1, datetime.datetime.utcnow(), before_trade_storage_dict),
                                        ProductHistoryUnit(3, datetime.datetime.utcnow(), StorageDict())]),
                                    width=0.15, height=0.3, depth=0.1))
        return Niche("Test niche", niche_commissions_dict, 0.1, products)

    @staticmethod
    def leftover_func(x) -> int:
        return int(- math.sin((x + 300_000) * 0.00001 - math.pi / 30) / (x + 200_000) * 7_500_000)

    def test_green_zone(self):
        calculator = FrequencyCalculator()
        niche: Niche = self.create_test_niche()
        x, y = calculator.get_frequency_stats(niche)
        calculator.get_green_trade_zone(niche, x, y)


if __name__ == '__main__':
    unittest.main()
