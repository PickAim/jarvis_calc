import unittest

from jorm.market.infrastructure import Niche, HandlerType, Warehouse, Address
from jorm.market.person import UserPrivilege, User

from jarvis_calc.calculators.economy_analyze import SimpleEconomyCalculator, SimpleEconomyCalculateData, \
    SimpleEconomyResult
from tests.base_test import BaseCalcTest


class EconomyAnalyzeTest(BaseCalcTest):
    def test_unit_economy_calc_with_jorm(self):
        calculator = SimpleEconomyCalculator()
        niche: Niche = self.create_test_niche()
        warehouse = Warehouse("warehouse", 1, HandlerType.MARKETPLACE, Address(), main_coefficient=50, products=[],
                              basic_logistic_to_customer_commission=55_00, additional_logistic_to_customer_commission=0,
                              logistic_from_customer_commission=33_00, basic_storage_commission=15,
                              additional_storage_commission=0, mono_palette_storage_commission=10)
        client = User(name="client", privilege=UserPrivilege.BASIC, profit_tax=0.06)
        result = calculator.calculate(
            SimpleEconomyCalculateData(
                product_exist_cost=300_00,
                cost_price=100_00,
                length=50,
                width=20,
                height=10,
                mass=1
            ),
            niche, warehouse)
        self.assertEqual(SimpleEconomyResult(result_cost=30000,
                                             logistic_price=3750,
                                             storage_price=10000,
                                             purchase_cost=10000,
                                             marketplace_expanses=19350,
                                             absolute_margin=650,
                                             relative_margin=0.021666666666666667,
                                             roi=0.065), result[0])
        self.assertEqual(SimpleEconomyResult(result_cost=67821,
                                             logistic_price=3750,
                                             storage_price=10000,
                                             purchase_cost=10000,
                                             marketplace_expanses=25779,
                                             absolute_margin=32042,
                                             relative_margin=0.4724495362793235,
                                             roi=3.2042), result[1])


if __name__ == '__main__':
    unittest.main()
