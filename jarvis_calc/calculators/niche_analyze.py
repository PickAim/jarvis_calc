import datetime
from dataclasses import dataclass

import numpy as np
from jorm.market.infrastructure import Niche
from jorm.market.items import Product
from jorm.support.constants import DAYS_IN_MONTH
from numpy import ndarray

from jarvis_calc.calculators.calculator_base import CalculatorBase
from jarvis_calc.utils.calculation_utils import calculate_trade_frequencies, calculate_trade_profits


@dataclass
class NicheCharacteristicsCalculateResult:
    card_count: int
    niche_profit: int
    card_trade_count: int
    mean_card_rating: float
    card_with_trades_count: int
    daily_mean_niche_profit: int
    daily_mean_trade_count: int
    mean_traded_card_cost: int
    month_mean_niche_profit_per_card: int
    monopoly_percent: float
    maximum_profit_idx: int


class NicheHistCalculator(CalculatorBase):
    @staticmethod
    def calculate(niche: Niche) -> tuple[list[int], list[int]]:
        cost_data: ndarray[int] = niche.cost_data.copy()
        n_samples: int = int(len(cost_data) * 0.1)
        return NicheHistWithNCalculator.calculate(cost_data, n_samples)


class NicheHistWithNCalculator(CalculatorBase):
    @staticmethod
    def calculate(cost_data: ndarray[int], n_samples: int) -> tuple[list[int], list[int]]:
        if len(cost_data) <= 0:
            return [], []
        base_keys, base_frequencies = NicheHistWithNCalculator.__frequency_calc(cost_data, n_samples)
        keys = base_keys.copy()
        frequencies = base_frequencies.copy()
        math_ozh: int = NicheHistWithNCalculator.__get_cleared_mean(frequencies)
        interesting_part_ind = len(keys) // 3
        if len(frequencies) < 2:
            return keys, frequencies
        while frequencies[interesting_part_ind] > math_ozh // 2 and interesting_part_ind < len(frequencies):
            interesting_part_ind += 1
        while True:
            if 0 < interesting_part_ind < len(frequencies):
                right_key = keys[interesting_part_ind]
                right_frequency: int = 0
                for i in range(interesting_part_ind, len(frequencies)):
                    right_frequency += frequencies[i]
                left_costs: list[float] = []
                for cost in cost_data:
                    if cost < keys[interesting_part_ind - 1]:
                        left_costs.append(cost)
                    else:
                        break
                keys, frequencies = NicheHistWithNCalculator.__frequency_calc(np.array(left_costs), n_samples - 1)
                keys.append(right_key)
                frequencies.append(right_frequency)
                if right_frequency > NicheHistWithNCalculator.__get_cleared_mean(frequencies):
                    interesting_part_ind += 1
                    frequencies = base_frequencies
                    keys = base_keys
                else:
                    break
            else:
                break
        return list(keys), list(frequencies)

    @staticmethod
    def __frequency_calc(costs: ndarray[int], n_samples: int) -> tuple[list[int], list[int]]:
        res = np.histogram(costs, n_samples)
        return list(map(int, res[1][1:])), list(res[0])

    @staticmethod
    def __get_cleared_mean(lst: list[int]) -> int:
        result: int = 0
        clear_frequency = np.array([x for x in lst if x != 0])
        for freq in clear_frequency:
            result += freq
        return int(result / len(clear_frequency))


class NicheCharacteristicsCalculator(CalculatorBase):
    @staticmethod
    def calculate(niche: Niche) -> NicheCharacteristicsCalculateResult:
        result_card_count: int = len(niche.products)
        result_products_with_trades_count = 0
        result_products_trade_count = 0
        traded_products_profit = 0
        rating_count = 0

        top_100_profit = 0
        freq_keys, _ = NicheHistWithNCalculator.calculate(niche.cost_data, 3)
        trade_profits = calculate_trade_profits(niche.products, freq_keys)
        max_idx = int(np.argmax(trade_profits))
        for product in niche.products:
            product_trade_count = product.history.get_last_month_trade_count()
            rating_count += product.rating
            if product_trade_count > 0:
                result_products_with_trades_count += 1
                result_products_trade_count += product_trade_count
                traded_products_profit += product_trade_count * product.cost
                if niche.name in product.top_places and product.top_places[niche.name] <= 100:
                    top_100_profit += product_trade_count * product.cost

        result_overall_profit = traded_products_profit
        return NicheCharacteristicsCalculateResult(
            card_count=result_card_count,
            niche_profit=int(result_overall_profit),
            card_trade_count=result_products_trade_count,
            mean_card_rating=rating_count / result_card_count,
            card_with_trades_count=result_products_with_trades_count,
            daily_mean_niche_profit=int(result_overall_profit / DAYS_IN_MONTH),
            daily_mean_trade_count=int(result_products_trade_count / DAYS_IN_MONTH),
            mean_traded_card_cost=int(result_overall_profit / result_products_trade_count),
            month_mean_niche_profit_per_card=int(result_overall_profit / result_card_count),
            monopoly_percent=top_100_profit / result_overall_profit,
            maximum_profit_idx=max_idx
        )


class GreenTradeZoneCalculator(CalculatorBase):
    @staticmethod
    def calculate(niche: Niche):
        freq_keys, frequencies = NicheHistCalculator.calculate(niche)
        products = niche.products
        trade_frequencies = calculate_trade_frequencies(products, freq_keys)

        # plot.plot(freq_keys, trade_frequencies)
        # plot.plot(freq_keys, frequencies)
        # plot.show()
