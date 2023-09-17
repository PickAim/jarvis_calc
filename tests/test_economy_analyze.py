import unittest

from jorm.market.infrastructure import Niche, HandlerType, Warehouse, Address
from jorm.market.person import UserPrivilege, User
from jorm.support.calculation import SimpleEconomyResult, TransitEconomyResult
from jorm.support.types import EconomyConstants

from jarvis_calc.calculators.economy_analyze import (
    SimpleEconomyCalculator,
    SimpleEconomyCalculateData,
    TransitEconomyCalculator,
    TransitEconomyCalculateData,
)
from jarvis_calc.calculators.niche_analyze import GreenTradeZoneCalculator
from tests.base_test import BaseCalcTest

ECONOMY_CONSTANT = EconomyConstants(
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


class EconomyAnalyzeTest(BaseCalcTest):
    def test_unit_economy_calc(self):
        calculator = SimpleEconomyCalculator(ECONOMY_CONSTANT)
        niche: Niche = self.create_test_niche()
        green_zone_result = GreenTradeZoneCalculator.calculate(niche)
        warehouse = Warehouse("warehouse", 1, HandlerType.MARKETPLACE, Address(), main_coefficient=0.5, products=[])
        result = calculator.calculate(
            SimpleEconomyCalculateData(
                product_exist_cost=300_00,
                cost_price=100_00,
                length=50,
                width=20,
                height=10,
                mass=1
            ),
            niche, warehouse, green_zone_result)
        self.assertEqual(SimpleEconomyResult(result_cost=300_00,
                                             logistic_price=37_50,
                                             storage_price=22,
                                             purchase_cost=100_00,
                                             marketplace_expanses=100_10,
                                             absolute_margin=99_90,
                                             relative_margin=0.333,
                                             roi=0.999), result[0])
        self.assertEqual(SimpleEconomyResult(result_cost=1334_25,
                                             logistic_price=37_50,
                                             storage_price=22,
                                             purchase_cost=100_00,
                                             marketplace_expanses=275_92,
                                             absolute_margin=958_33,
                                             relative_margin=0.7182537005808507,
                                             roi=9.5833), result[1])

    def test_transit_unit_economy_calc(self):
        calculator = TransitEconomyCalculator(ECONOMY_CONSTANT)
        niche: Niche = self.create_test_niche()
        green_zone_result = GreenTradeZoneCalculator.calculate(niche)
        warehouse = Warehouse("warehouse", 1, HandlerType.MARKETPLACE, Address(), main_coefficient=0.5, products=[])
        client = User(name="client", privilege=UserPrivilege.BASIC, profit_tax=0.06)
        result = calculator.calculate(
            TransitEconomyCalculateData(
                product_exist_cost=300_00,
                cost_price=100_00,
                length=50,
                width=20,
                height=10,
                mass=1,

                logistic_count=100,
                logistic_price=5000_00,
                transit_cost_for_cubic_meter=10_00
            ),
            niche, client, warehouse, green_zone_result)
        self.assertEqual(TransitEconomyResult(result_cost=300_00,
                                              logistic_price=37_50,
                                              storage_price=22,
                                              purchase_cost=150_00,
                                              marketplace_expanses=100_10,
                                              absolute_margin=49_90,
                                              relative_margin=0.16633333333333333,
                                              roi=0.33266666666666667,
                                              purchase_investments=15000_00,
                                              commercial_expanses=10010_00,
                                              tax_expanses=1800_00,
                                              absolute_transit_margin=3190_00,
                                              relative_transit_margin=0.10633333333333334,
                                              transit_roi=0.21266666666666667), result[0])
        self.assertEqual(TransitEconomyResult(result_cost=1334_25,
                                              logistic_price=37_50,
                                              storage_price=22,
                                              purchase_cost=150_00,
                                              marketplace_expanses=275_92,
                                              absolute_margin=908_33,
                                              relative_margin=0.6807794641184186,
                                              roi=6.055533333333333,
                                              purchase_investments=15000_00,
                                              commercial_expanses=27592_00,
                                              tax_expanses=8005_50,
                                              absolute_transit_margin=82827_50,
                                              relative_transit_margin=0.6207794641184186,
                                              transit_roi=5.521833333333333), result[1])


if __name__ == '__main__':
    unittest.main()
