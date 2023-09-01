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
        warehouse = Warehouse("warehouse", 1, HandlerType.MARKETPLACE, Address(), main_coefficient=0.5, products=[],
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
        self.assertEqual(SimpleEconomyResult(result_cost=300_00,
                                             logistic_price=37_50,
                                             storage_price=90,
                                             purchase_cost=100_00,
                                             marketplace_expanses=120_50,
                                             absolute_margin=79_50,
                                             relative_margin=0.265,
                                             roi=0.795), result[0])
        self.assertEqual(SimpleEconomyResult(result_cost=495_93,
                                             logistic_price=37_50,
                                             storage_price=90,
                                             purchase_cost=100_00,
                                             marketplace_expanses=153_80,
                                             absolute_margin=242_13,
                                             relative_margin=0.4882342266045611,
                                             roi=2.4213), result[1])


if __name__ == '__main__':
    unittest.main()
