import unittest

from jorm.market.infrastructure import Niche

from jarvis_calc.calculators.niche_analyze import NicheAnalyzeCalculator
from tests.base_test import BaseCalcTest
from tests.data_for_tests import cost_data


class NicheAnalyzeTest(BaseCalcTest):
    def test_only_freq_calc_with_jorm(self):
        calculator = NicheAnalyzeCalculator()
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

    def test_niche_analyze_parameters(self):
        calculator = NicheAnalyzeCalculator()
        niche: Niche = self.create_test_niche()
        self.assertEqual({
            'card_count': 4114,
            'niche_profit': 7558992306.683339,
            'card_trade_count': 54972,
            'mean_card_rating': 4.0,
            'card_with_trades_count': 3875,
            'daily_mean_niche_profit': 251966410,
            'daily_mean_trade_count': 1832,
            'mean_traded_card_cost': 137506,
            'month_mean_niche_profit_per_card': 1837382,
            'monopoly_percent': 0.030747309758626423,
            'maximum_profit_idx': 1}, calculator.calculate_niche_characteristic(niche))

    def test_green_zone(self):
        calculator = NicheAnalyzeCalculator()
        niche: Niche = self.create_test_niche()
        calculator.get_green_trade_zone(niche)


if __name__ == '__main__':
    unittest.main()
