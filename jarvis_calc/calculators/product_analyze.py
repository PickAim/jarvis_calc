import datetime as date_root
from datetime import datetime

from jorm.market.items import Product, ProductHistoryUnit
from jorm.support.constants import DAYS_IN_MONTH

from jarvis_calc.calculators.calculator_base import Calculator


class DownturnCalculator(Calculator):
    @classmethod
    def calculate(cls, product: Product, from_date) -> dict[int, dict[str, int]]:
        warehouse_id_to_downturn_days: dict[int, dict[str, int]] = {}
        all_leftovers = product.history.get_all_mapped_leftovers()
        downturns = product.history.get_leftovers_downturn(from_date)
        for warehouse_id in downturns:
            if warehouse_id in all_leftovers:
                if warehouse_id not in warehouse_id_to_downturn_days:
                    warehouse_id_to_downturn_days[warehouse_id] = {}
                for specify in downturns[warehouse_id]:
                    if specify in all_leftovers[warehouse_id]:
                        mean_downturn = \
                            abs(downturns[warehouse_id][specify].sum // downturns[warehouse_id][specify].count)
                        warehouse_id_to_downturn_days[warehouse_id][specify] = \
                            all_leftovers[warehouse_id][specify] // mean_downturn if mean_downturn > 0 else -1
                    else:
                        warehouse_id_to_downturn_days[warehouse_id][specify] = 0
        return warehouse_id_to_downturn_days


class TurnoverCalculator(Calculator):
    @classmethod
    def calculate(cls, product: Product, from_date) -> dict[int, dict[str, float]]:
        warehouse_id_to_turnover: dict[int, dict[str, float]] = {}
        start_history_unit = cls.__find_history_unit_to_calc(product.history.get_history(), from_date)
        start_leftovers = start_history_unit.leftover.get_mapped_leftovers()
        end_leftovers = product.history.get_all_mapped_leftovers()
        leftovers_half_sum = \
            cls.__calc_half_sum_of_leftovers(start_leftovers, end_leftovers, (lambda x, y: (x + y) / 2))
        downturns = product.history.get_leftovers_downturn(from_date)
        for warehouse_id in downturns:
            if warehouse_id in leftovers_half_sum:
                for specify in downturns[warehouse_id]:
                    if specify in leftovers_half_sum[warehouse_id]:
                        downturn_sum = abs(downturns[warehouse_id][specify].sum)
                        if warehouse_id not in warehouse_id_to_turnover:
                            warehouse_id_to_turnover[warehouse_id] = {}
                        warehouse_id_to_turnover[warehouse_id][specify] = \
                            DAYS_IN_MONTH \
                            * (leftovers_half_sum[warehouse_id][specify] / downturn_sum) if downturn_sum > 0 else 0
        return warehouse_id_to_turnover

    @classmethod
    def __calc_half_sum_of_leftovers(cls, first: dict[int, dict[str, int]],
                                     second: dict[int, dict[str, int]], lambda_func) -> dict[int, dict[str, int]]:
        first_set = set(first)
        second_set = set(second)
        return {
            k: cls.__map_any_leftovers(first.get(k, {}), second.get(k, {}), lambda_func)
            for k in first_set | second_set
        }

    @classmethod
    def __map_any_leftovers(cls, first: dict[str, int],
                            second: dict[str, int], lambda_func) -> dict[str, int]:
        first_set = set(first)
        second_set = set(second)
        return {
            k: lambda_func(first.get(k, 0), second.get(k, 0))
            for k in first_set | second_set
        }

    @classmethod
    def __find_history_unit_to_calc(cls, history: list[ProductHistoryUnit], from_date: datetime) -> ProductHistoryUnit:
        date_to_stop = from_date - date_root.timedelta(DAYS_IN_MONTH)
        for i in range(len(history) - 1, 0):
            if history[i].unit_date < date_to_stop:
                return history[i]
        return history[0]
