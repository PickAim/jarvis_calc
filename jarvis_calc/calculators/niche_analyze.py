import datetime

import numpy as np
from jorm.market.infrastructure import Niche
from jorm.market.items import Product
from jorm.support.calculation import NicheCharacteristicsCalculateResult, GreenTradeZoneCalculateResult
from jorm.support.constants import DAYS_IN_MONTH
from numpy import ndarray

from jarvis_calc.calculators.calculator_base import Calculator


class NicheHistCalculator(Calculator):
    @classmethod
    def calculate(cls, niche: Niche) -> tuple[list[int], list[int]]:
        cost_data: ndarray[int] = niche.cost_data.copy()
        n_samples: int = 10
        return NicheHistWithNCalculator.calculate(cost_data, n_samples)


class NicheHistWithNCalculator(Calculator):
    @classmethod
    def calculate(cls, cost_data: ndarray[int], n_samples: int) -> tuple[list[int], list[int]]:
        if len(cost_data) <= 0:
            return [], []
        return cls.__frequency_calc(cost_data, n_samples)
        # possible needed to correct frequencies, disabled for now
        # base_keys, base_frequencies = NicheHistWithNCalculator.__frequency_calc(cost_data, n_samples)
        # keys = base_keys.copy()
        # frequencies = base_frequencies.copy()
        # math_ozh: int = NicheHistWithNCalculator.__get_cleared_mean(frequencies)
        # interesting_part_ind = len(keys) // 3
        # if len(frequencies) < 2:
        #     return keys, frequencies
        # while frequencies[interesting_part_ind] > math_ozh // 2 and interesting_part_ind < len(frequencies):
        #     interesting_part_ind += 1
        # while True:
        #     if 0 < interesting_part_ind < len(frequencies):
        #         right_key = keys[interesting_part_ind]
        #         right_frequency: int = 0
        #         for i in range(interesting_part_ind, len(frequencies)):
        #             right_frequency += frequencies[i]
        #         left_costs: list[float] = []
        #         for cost in cost_data:
        #             if cost < keys[interesting_part_ind - 1]:
        #                 left_costs.append(cost)
        #             else:
        #                 break
        #         keys, frequencies = NicheHistWithNCalculator.__frequency_calc(np.array(left_costs), n_samples - 1)
        #         keys.append(right_key)
        #         frequencies.append(right_frequency)
        #         if right_frequency > NicheHistWithNCalculator.__get_cleared_mean(frequencies):
        #             interesting_part_ind += 1
        #             frequencies = base_frequencies
        #             keys = base_keys
        #         else:
        #             break
        #     else:
        #         break
        # return list(keys), list(frequencies)

    @classmethod
    def __frequency_calc(cls, costs: ndarray[int], n_samples: int) -> tuple[list[int], list[int]]:
        res = np.histogram(costs, n_samples)
        return list(map(int, res[1][:-1])), list(res[0])

    @classmethod
    def __get_cleared_mean(cls, lst: list[int]) -> int:
        result: int = 0
        clear_frequency = np.array([x for x in lst if x != 0])
        for freq in clear_frequency:
            result += freq
        return int(result / len(clear_frequency))


class NicheCharacteristicsCalculator(Calculator):
    @classmethod
    def calculate(cls, niche: Niche) -> NicheCharacteristicsCalculateResult:
        result_card_count: int = len(niche.products)
        result_products_with_trades_count = 0
        result_products_trade_count = 0
        traded_products_profit = 0
        rating_count = 0

        top_100_profit = 0
        freq_keys, _ = NicheHistWithNCalculator.calculate(niche.cost_data, 10)
        trade_profits = cls.__calculate_trade_profits(niche.products, freq_keys)
        max_idx = 0 if len(trade_profits) == 0 else int(np.argmax(trade_profits))
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
            mean_card_rating=0 if result_card_count == 0 else rating_count / result_card_count,
            card_with_trades_count=result_products_with_trades_count,
            daily_mean_niche_profit=int(result_overall_profit / DAYS_IN_MONTH),
            daily_mean_trade_count=int(result_products_trade_count / DAYS_IN_MONTH),
            mean_traded_card_cost=0 if result_products_trade_count == 0 else int(
                result_overall_profit / result_products_trade_count),
            month_mean_niche_profit_per_card=0 if result_card_count == 0 else int(
                result_overall_profit / result_card_count),
            monopoly_percent=0 if result_overall_profit == 0 else top_100_profit / result_overall_profit,
            maximum_profit_idx=max_idx
        )

    @classmethod
    def __calculate_trade_profits(cls, products: list[Product], freq_keys: list[int],
                                  from_date: datetime.datetime = datetime.datetime.utcnow()) -> list[int]:
        trade_profits: list[int] = [0 for _ in range(len(freq_keys))]
        sorted_products = sorted(products, key=lambda prod: prod.cost, reverse=True)
        j = len(freq_keys) - 1
        for i, product in enumerate(sorted_products):
            if j < 0 or j >= len(trade_profits):
                break
            if product.cost < freq_keys[j]:
                j -= 1
            trade_profits[j] += product.history.get_last_month_trade_count(from_date) * product.cost
        return trade_profits


class GreenTradeZoneCalculator(Calculator):
    @classmethod
    def calculate(cls, niche: Niche,
                  from_date: datetime.datetime = datetime.datetime.utcnow()) -> GreenTradeZoneCalculateResult:
        res = np.histogram(niche.cost_data, 10)
        freq_keys, frequencies = list(map(int, res[1][:-1])), list(map(int, res[0]))
        sorted_products = sorted(niche.products, key=lambda prod: prod.cost, reverse=True)

        segment_profits: list[int] = [0 for _ in range(len(freq_keys))]
        product_with_profit_counts: list[int] = [0 for _ in range(len(freq_keys))]
        j = len(freq_keys) - 1
        for i, product in enumerate(sorted_products):
            if j < 0 or j >= len(segment_profits):
                break
            if product.cost < freq_keys[j]:
                j -= 1
            product_profit = int(product.history.get_last_month_trade_count(from_date) * product.cost)
            if product_profit > 0:
                product_with_profit_counts[j] += 1
                segment_profits[j] += product_profit

        segments: list[tuple[int, int]] = [(freq_keys[i], freq_keys[i + 1]) for i in range(len(freq_keys) - 1)]
        segments.append((freq_keys[len(freq_keys) - 1], sorted_products[0].cost if len(sorted_products) > 0 else 0))

        mean_segment_profit: list[int] = [
            segment_profits[i] // frequencies[i] if frequencies[i] != 0 else 0
            for i in range(len(segment_profits))
        ]
        mean_product_profit: list[int] = [
            segment_profits[i] // product_with_profit_counts[i] if product_with_profit_counts[i] != 0 else 0
            for i in range(len(segment_profits))
        ]
        best_segment_profit_idx: int = int(np.argmax(segment_profits))
        best_mean_segment_profit_idx: int = int(np.argmax(mean_segment_profit))
        best_mean_product_profit_idx: int = int(np.argmax(mean_product_profit))
        best_segment_product_count_idx: int = int(np.argmin(frequencies))
        best_segment_product_with_trades_count_idx: int = int(np.argmax(product_with_profit_counts))

        counter = {}
        for integer in [best_segment_profit_idx, best_mean_segment_profit_idx,
                        best_mean_product_profit_idx, best_segment_product_count_idx,
                        best_segment_product_with_trades_count_idx]:
            if integer not in counter:
                counter[integer] = 0
            counter[integer] += 1

        best_segment_idx: int = max(counter, key=counter.get)
        return GreenTradeZoneCalculateResult(
            segments=segments,
            best_segment_idx=best_segment_idx,
            segment_profits=segment_profits,
            best_segment_profit_idx=best_segment_profit_idx,
            mean_segment_profit=mean_segment_profit,
            best_mean_segment_profit_idx=best_mean_segment_profit_idx,
            mean_product_profit=mean_product_profit,
            best_mean_product_profit_idx=best_mean_product_profit_idx,
            segment_product_count=frequencies,
            best_segment_product_count_idx=best_segment_product_count_idx,
            segment_product_with_trades_count=product_with_profit_counts,
            best_segment_product_with_trades_count_idx=best_segment_product_with_trades_count_idx
        )
