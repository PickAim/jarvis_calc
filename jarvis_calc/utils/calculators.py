import numpy as np
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import Client
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

    def get_frequency_stats(self, niche: Niche) -> tuple[list[float], list[int]]:
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


class UnitEconomyCalculator:
    def __init__(self):
        self.__SAMPLES_COUNT: int = 20
        self.__MONTH: int = 30

    def calc_unit_economy(self, buy_price: int,
                          pack_price: int,
                          niche: Niche,
                          warehouse: Warehouse,
                          client: Client,
                          transit_price: int = 0.0,
                          transit_count: int = 0.0,
                          market_place_transit_price: int = 0.0) -> dict:
        niche_commission: float = warehouse.get_niche_commission(niche)
        unit_cost: int = (buy_price + pack_price)
        mean_concurrent_cost: int = niche.get_mean_concurrent_cost(unit_cost,
                                                                   warehouse.basic_logistic_to_customer_commission,
                                                                   warehouse.basic_storage_commission)
        result_commission: int = int(mean_concurrent_cost * niche_commission)
        result_logistic_price: int = warehouse.basic_logistic_to_customer_commission
        result_storage_price = warehouse.basic_storage_commission

        revenue: int = 1
        investments: int = 1
        result_transit_profit: int = 0

        if transit_count > 0:
            result_logistic_price += (transit_price + market_place_transit_price) / transit_count
            result_storage_price = self.__MONTH * result_storage_price

            volume: float = niche.get_mean_product_volume()
            logistic_expanses: int = market_place_transit_price
            if market_place_transit_price == 0:
                logistic_expanses = \
                    warehouse.calculate_logistic_price_for_one(volume, niche.returned_percent) * transit_count

            revenue = mean_concurrent_cost * transit_count
            investments = unit_cost * transit_count
            marketplace_expenses: int = int(revenue * niche_commission + logistic_expanses
                                            + warehouse.calculate_storage_price(volume) * transit_count)
            result_transit_profit = revenue - investments - marketplace_expenses - int(
                revenue * client.get_profit_tax())

        result_product_margin: int = (mean_concurrent_cost - result_commission
                                      - result_logistic_price - result_storage_price - unit_cost)

        return {
            "Pcost": (buy_price, float(buy_price) / mean_concurrent_cost),  # Закупочная себестоимость
            "Pack": (pack_price, float(pack_price) / mean_concurrent_cost),  # Упаковка
            "Mcomm": (result_commission, float(result_commission) / mean_concurrent_cost),  # Комиссия маркетплейса
            "Log": (result_logistic_price, float(result_logistic_price) / mean_concurrent_cost),  # Логистика
            "Store": (result_storage_price, float(result_storage_price) / mean_concurrent_cost),  # Хранение
            "Margin": (result_product_margin, float(result_product_margin) / mean_concurrent_cost),  # Маржа в копейках
            "RecommendedPrice": (buy_price + pack_price + result_commission + result_logistic_price +
                                 result_storage_price + result_product_margin),
            "TProfit": (result_transit_profit, 1.0),  # Чистая прибыль с транзита
            "ROI": (result_transit_profit / investments, 1.0),  # ROI
            "TMargin": (result_transit_profit / revenue, 1.0)  # Маржа с транзита (%)
        }
