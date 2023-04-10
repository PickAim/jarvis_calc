import datetime

import numpy as np
from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import Client
from jorm.support.constants import DAYS_IN_MONTH
from matplotlib import pyplot as plot
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

        plot.plot(freq_keys, trade_frequencies)
        plot.plot(freq_keys, frequencies)
        plot.show()


class UnitEconomyCalculator:
    @staticmethod
    def calc_unit_economy(buy_price: int,
                          pack_price: int,
                          niche: Niche,
                          warehouse: Warehouse,
                          client: Client,
                          transit_price: int = 0.0,
                          transit_count: int = 0.0,
                          market_place_transit_price: int = 0.0) -> dict[str, int]:
        niche_commission: float = warehouse.get_niche_commission(niche)
        unit_cost: int = (buy_price + pack_price)
        mean_concurrent_cost: int = niche.get_mean_concurrent_cost(unit_cost,
                                                                   warehouse.basic_logistic_to_customer_commission,
                                                                   warehouse.basic_storage_commission)
        result_commission: int = int(mean_concurrent_cost * niche_commission)
        result_logistic_price: int = warehouse.basic_logistic_to_customer_commission
        result_storage_price: int = warehouse.basic_storage_commission

        revenue: int = 1
        investments: int = 1
        result_transit_profit: int = 0

        if transit_count > 0:
            result_logistic_price += (transit_price + market_place_transit_price) // transit_count
            result_storage_price = DAYS_IN_MONTH * result_storage_price

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
            "product_cost": buy_price,  # Закупочная себестоимость
            "pack_cost": pack_price,  # Упаковка
            "marketplace_commission": result_commission,  # Комиссия маркетплейса
            "logistic_price": result_logistic_price,  # Логистика
            "storage_price": result_storage_price,  # Хранение
            "margin": result_product_margin,  # Маржа в копейках
            "recommended_price": (buy_price + pack_price + result_commission + result_logistic_price +
                                  result_storage_price + result_product_margin),
            "transit_profit": result_transit_profit,  # Чистая прибыль с транзита
            "roi": result_transit_profit // investments,  # ROI
            "transit_margin": result_transit_profit // revenue,  # Маржа с транзита (%)
        }
