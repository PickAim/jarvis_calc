import unittest

import matplotlib.pyplot as plot
from jorm.market.infrastructure import Niche

from jarvis_calc.calculators.niche_analyze import NicheCharacteristicsCalculator, NicheHistCalculator, \
    NicheCharacteristicsCalculateResult, GreenTradeZoneCalculator, GreenTradeZoneCalculateResult
from tests.base_test import BaseCalcTest
from tests.data_for_tests import cost_data


class NicheAnalyzeTest(BaseCalcTest):
    def test_only_freq_calc_with_jorm(self):
        niche: Niche = self.create_test_niche()
        x, y = NicheHistCalculator.calculate(niche)
        self.assertEqual(int(len(cost_data) * 0.1), len(x))

    def test_mean_concurrent_cost_calc_with_niche(self):
        niche: Niche = self.create_test_niche()
        buy = 500_00
        pack = 150_00
        unit_cost: int = buy + pack
        mid_cost: int = niche.get_mean_concurrent_cost(unit_cost, 5500, 15)
        self.assertEqual(971_23, mid_cost)

    def test_niche_analyze_parameters(self):
        niche: Niche = self.create_test_niche()
        result = NicheCharacteristicsCalculator.calculate(niche)
        self.assertEqual(NicheCharacteristicsCalculateResult(
            card_count=4114,
            niche_profit=7558992306,
            card_trade_count=54972,
            mean_card_rating=4.0,
            card_with_trades_count=3875,
            daily_mean_niche_profit=251966410,
            daily_mean_trade_count=1832,
            mean_traded_card_cost=137506,
            month_mean_niche_profit_per_card=1837382,
            monopoly_percent=0.030747309758626423,
            maximum_profit_idx=0), result)

    def test_green_zone(self):
        niche: Niche = self.create_test_niche()
        result = GreenTradeZoneCalculator.calculate(niche)
        # self.draw_green_zone_result(result) # uncomment if you need draw results
        self.assertEqual([(263550, 523800), (523800, 784050), (784050, 1044300),
                          (1044300, 1304550), (1304550, 1564800), (1564800, 1825050),
                          (1825050, 2085300), (2085300, 2345550), (2345550, 2605800), (2605800, 2605800.0)],
                         result.segments)
        self.assertEqual([224035864, 40938752, 79150750, 0, 0, 0, 4103700, 0, 3945400, 5499900], result.segment_profits)
        self.assertEqual([59034, 162455, 1978768, 0, 0, 0, 0, 0, 0, 5499900], result.mean_segment_profit)
        self.assertEqual([1851536, 3411562, 4655926, 0, 0, 0, 4103700, 0, 3945400, 2749950], result.mean_product_profit)
        self.assertEqual([3795, 252, 40, 19, 4, 1, 0, 2, 0, 1], result.segment_product_count)
        self.assertEqual([121, 12, 17, 0, 0, 0, 1, 0, 1, 2], result.segment_product_with_trades_count)

    def draw_green_zone_result(self, result: GreenTradeZoneCalculateResult):
        keys_to_draw = [key[0] // 100 for key in result.segments]
        segment_profits_to_draw = [key // 100_000 for key in result.segment_profits]
        mean_segment_profits_to_draw = [key // 100 for key in result.mean_segment_profit]
        mean_segment_product_profit_to_draw = [key // 100 for key in result.mean_product_profit]
        segment_product_count_to_draw = [key for key in result.segment_product_count]
        segment_product_with_trades_count_to_draw = [key for key in result.segment_product_with_trades_count]

        figure = plot.figure()

        figure.add_subplot(2, 3, 3)
        plot.title("Segment profits")
        self.draw_zone(result.best_segment_profit_idx, keys_to_draw)
        plot.plot(keys_to_draw, segment_profits_to_draw)
        plot.grid()

        figure.add_subplot(2, 3, 1)
        plot.title("Mean segment profits")
        self.draw_zone(result.best_mean_segment_profit_idx, keys_to_draw)
        plot.plot(keys_to_draw, mean_segment_profits_to_draw)
        plot.grid()

        figure.add_subplot(2, 3, 2)
        plot.title("Mean product profit")
        self.draw_zone(result.best_mean_product_profit_idx, keys_to_draw)
        plot.plot(keys_to_draw, mean_segment_product_profit_to_draw)
        plot.grid()

        figure.add_subplot(2, 3, 5)
        plot.title("Product counts")
        self.draw_zone(result.best_segment_product_count_idx, keys_to_draw)
        plot.plot(keys_to_draw, segment_product_count_to_draw)
        plot.grid()

        figure.add_subplot(2, 3, 4)
        plot.title("Products with trade counts")
        self.draw_zone(result.best_segment_product_with_trades_count_idx, keys_to_draw)
        plot.plot(keys_to_draw, segment_product_with_trades_count_to_draw)
        plot.grid()

        subplot = figure.add_subplot(2, 3, 6)
        plot.title("Result recommendation")
        grid_ticks = [keys_to_draw[i] for i in range(0, len(keys_to_draw), 2)]
        grid_ticks.append(keys_to_draw[len(keys_to_draw) - 1] + keys_to_draw[0])
        grid_ticks.append(keys_to_draw[result.best_segment_idx])
        grid_ticks.append(keys_to_draw[result.best_segment_idx + 1])
        subplot.set_xticks(grid_ticks)
        plot.axvline(x=keys_to_draw[result.best_segment_idx], color='lime', label=f'best zone')
        plot.axvline(x=keys_to_draw[result.best_segment_idx + 1], color='lime', label=f'best zone')
        plot.grid()

        plot.show()

    @staticmethod
    def draw_zone(idx: int, keys_to_draw: list[int]):
        for i in range(len(keys_to_draw)):
            if i == idx or i == idx + 1:
                plot.axvline(x=keys_to_draw[i], color='lime', label=f'zone {i}')
            else:
                plot.axvline(x=keys_to_draw[i], color='r', label=f'zone {i}')


if __name__ == '__main__':
    unittest.main()
