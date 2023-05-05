import unittest

from jorm.market.infrastructure import Niche

from jarvis_calc.calculators.niche_analyze import FrequencyCalculator
from tests.base_test import BaseCalcTest
from tests.data_for_tests import cost_data


class NicheAnalyzeTest(BaseCalcTest):
    def test_only_freq_calc_with_jorm(self):
        calculator = FrequencyCalculator()
        niche: Niche = self.create_test_niche()
        x, y = calculator.calculate_niche_hist(niche)
        self.assertEqual(int(len(cost_data) * 0.1), len(x))

    def test_mean_concurrent_cost_calc_with_niche(self):
        niche: Niche = self.create_test_niche()
        buy = 500_00
        pack = 150_00
        unit_cost: int = buy + pack
        mid_cost: int = niche.get_mean_concurrent_cost(unit_cost, 5500, 15)
        self.assertEqual(971_23, mid_cost)

    def test_green_zone(self):
        calculator = FrequencyCalculator()
        niche: Niche = self.create_test_niche()
        x, y = calculator.calculate_niche_hist(niche)
        calculator.get_green_trade_zone(niche, x, y)


if __name__ == '__main__':
    unittest.main()
