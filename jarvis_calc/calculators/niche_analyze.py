import datetime

import numpy as np
from jorm.market.infrastructure import Niche
from jorm.support.constants import DAYS_IN_MONTH
from numpy import ndarray


class FrequencyCalculator:
    @staticmethod
    def __frequency_calc(costs: ndarray[float], n_samples: int) -> tuple[list[float], list[int]]:
        res = np.histogram(costs, n_samples)
        return list(res[1][1:]), list(res[0])

    @staticmethod
    def __get_cleared_mean(lst: list[int]) -> int:
        result: int = 0
        clear_frequency = np.array([x for x in lst if x != 0])
        for freq in clear_frequency:
            result += freq
        return int(result / len(clear_frequency))

    def calculate_niche_hist(self, niche: Niche) -> tuple[list[float], list[int]]:
        cost_data: ndarray[float] = niche.cost_data.copy()
        n_samples: int = int(len(cost_data) * 0.1)
        if len(cost_data) <= 0:
            return [], []
        base_keys, base_frequencies = self.__frequency_calc(cost_data, n_samples)
        keys = base_keys.copy()
        frequencies = base_frequencies.copy()
        math_ozh: int = self.__get_cleared_mean(frequencies)
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
                keys, frequencies = self.__frequency_calc(np.array(left_costs), n_samples - 1)
                keys.append(right_key)
                frequencies.append(right_frequency)
                if right_frequency > self.__get_cleared_mean(frequencies):
                    interesting_part_ind += 1
                    frequencies = base_frequencies
                    keys = base_keys
                else:
                    break
            else:
                break
        return list(map(int, keys)), list(map(int, frequencies))

    @staticmethod
    def calculate_niche_characteristic(niche: Niche) -> dict[str, int | float]:
        result_card_count: int = len(niche.products)
        result_products_with_trades_count = 0
        result_products_trade_count = 0
        traded_products_profit = 0
        rating_count = 0

        for product in niche.products:
            product_trade_count = product.history.get_last_month_trade_count()
            rating_count += product.rating
            if product_trade_count > 0:
                result_products_with_trades_count += 1
                result_products_trade_count += product_trade_count
                traded_products_profit += product_trade_count * product.cost
        result_overall_profit = traded_products_profit

        return {
            'card_count': result_card_count,
            'niche_profit': result_overall_profit,
            'card_trade_count': result_products_trade_count,
            'mean_card_rating': rating_count / result_card_count,
            'card_with_trades_count': result_products_with_trades_count,
            'month_mean_niche_profit': int(result_overall_profit / DAYS_IN_MONTH),
            'month_mean_trade_count': int(result_products_trade_count / DAYS_IN_MONTH),
            'mean_traded_card_cost': int(result_overall_profit / result_products_trade_count),
            'month_mean_niche_profit_per_card': int(result_overall_profit / result_card_count)
        }

    @staticmethod
    def get_green_trade_zone(niche: Niche, freq_keys: list[float],
                             frequencies: list[int], from_date: datetime.datetime = datetime.datetime.utcnow()):
        products = niche.products
        trade_frequencies: list[int] = [0 for _ in range(len(frequencies))]
        sorted_products = sorted(products, key=lambda prod: prod.cost, reverse=True)
        j = len(freq_keys) - 1
        for i, product in enumerate(sorted_products):
            if product.cost < freq_keys[j]:
                j -= 1
            trade_frequencies[j] = product.history.get_last_month_trade_count(from_date)

        # plot.plot(freq_keys, trade_frequencies)
        # plot.plot(freq_keys, frequencies)
        # plot.show()
