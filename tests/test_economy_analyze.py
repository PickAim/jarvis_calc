import unittest

from jorm.market.infrastructure import Niche, HandlerType, Warehouse, Address
from jorm.market.person import ClientInfo, UserPrivilege, User

from jarvis_calc.calculators.economy_analyze import UnitEconomyCalculator
from tests.base_test import BaseCalcTest


class EconomyAnalyzeTest(BaseCalcTest):
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
        client = User(name="client", privilege=UserPrivilege.BASIC, client_info=ClientInfo(profit_tax=0.06))
        result = calculator.calculate(buy, pack, niche, warehouse, client,
                                      transit_price, transit_count, marketplace_transit_price)
        self.assertEqual(69_57, result["margin"])


if __name__ == '__main__':
    unittest.main()
