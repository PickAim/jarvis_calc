import unittest

from jorm.market.infrastructure import Niche, HandlerType

from jarvis_calc.calculators.niche_analyze import FrequencyCalculator
from jarvis_calc.utils.temporary import get_commission_for, get_return_percent_for
from tests.base_test import BaseCalcTest
from tests.data_for_tests import cost_data


class NicheAnalyzeTest(BaseCalcTest):
    def test_only_freq_calc_with_jorm(self):
        calculator = FrequencyCalculator()
        niche: Niche = self.create_test_niche()
        x, y = calculator.calculate(niche)
        self.assertEqual(int(len(cost_data) * 0.1), len(x))

    def test_mean_concurrent_cost_calc_with_niche(self):
        niche: Niche = self.create_test_niche()
        buy = 500_00
        pack = 150_00
        unit_cost: int = buy + pack
        mid_cost: int = niche.get_mean_concurrent_cost(unit_cost, 5500, 15)
        self.assertEqual(971_23, mid_cost)

    def test_niche_info_load(self):
        commission: float = get_commission_for("Автомобильные товары",
                                               "Подстаканники электрические", str(HandlerType.MARKETPLACE))
        self.assertEqual(0.17, commission)
        return_percent: float = get_return_percent_for("Автомобильные товары", "Подстаканники электрические")
        self.assertEqual(0.1, return_percent)

    def test_green_zone(self):
        calculator = FrequencyCalculator()
        niche: Niche = self.create_test_niche()
        x, y = calculator.calculate(niche)
        calculator.get_green_trade_zone(niche, x, y)


if __name__ == '__main__':
    unittest.main()
