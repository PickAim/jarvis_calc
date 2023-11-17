import datetime as date_root
from dataclasses import dataclass
from datetime import datetime

from jorm.market.items import Product, ProductHistoryUnit
from jorm.support.constants import DAYS_IN_MONTH
from jorm.support.types import DownturnSumCount, DownturnMap

from jarvis_calc.calculators.calculator_base import Calculator


@dataclass
class DownturnInfo:
    leftover: int
    days: int


class DownturnCalculator(Calculator):
    def calculate(self, product: Product, from_date) -> dict[int, dict[str, DownturnInfo]]:
        warehouse_id_to_downturn_days: dict[int, dict[str, DownturnInfo]] = {}
        all_leftovers = product.history.get_all_mapped_leftovers()
        downturns = product.history.get_leftovers_downturn(from_date)
        for warehouse_id in downturns:
            if warehouse_id not in all_leftovers:
                continue
            if warehouse_id not in warehouse_id_to_downturn_days:
                warehouse_id_to_downturn_days[warehouse_id] = {}
            self.__fill_downturn_dict(warehouse_id, all_leftovers,
                                      downturns, warehouse_id_to_downturn_days[warehouse_id])
        return warehouse_id_to_downturn_days

    def __fill_downturn_dict(self, warehouse_id: int,
                             all_leftovers: dict[int, dict[str, int]],
                             downturns: dict[int, DownturnMap],
                             specify_to_downturn_days: dict[str, DownturnInfo]):
        specify_to_leftover = all_leftovers[warehouse_id]
        specify_to_downturn_map = downturns[warehouse_id]
        for specify in specify_to_downturn_map:
            if specify in specify_to_leftover:
                downturn_info = DownturnInfo(specify_to_leftover[specify],
                                             self.__calc_downturn_days(specify_to_downturn_map[specify],
                                                                       specify_to_leftover[specify]))
                specify_to_downturn_days[specify] = downturn_info
            else:
                specify_to_downturn_days[specify] = DownturnInfo(0, 0)

    @staticmethod
    def __calc_downturn_days(downturn_sum_count: DownturnSumCount, leftovers: int) -> int:
        mean_downturn = (0 if downturn_sum_count.count == 0
                         else abs(downturn_sum_count.sum // downturn_sum_count.count))
        return leftovers // mean_downturn if mean_downturn > 0 else -1


class TurnoverCalculator(Calculator):
    def calculate(self, product: Product, from_date) -> dict[int, dict[str, float]]:
        warehouse_id_to_turnover: dict[int, dict[str, float]] = {}
        start_history_unit = self.__find_history_unit_to_calc(product.history.get_history(), from_date)
        start_leftovers = start_history_unit.leftover.get_mapped_leftovers()
        end_leftovers = product.history.get_all_mapped_leftovers()
        leftovers_half_sum = \
            self.__calc_half_sum_of_leftovers(start_leftovers, end_leftovers, (lambda x, y: (x + y) / 2))
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

    def __calc_half_sum_of_leftovers(self, first: dict[int, dict[str, int]],
                                     second: dict[int, dict[str, int]], lambda_func) -> dict[int, dict[str, int]]:
        first_set = set(first)
        second_set = set(second)
        return {
            k: self.__map_any_leftovers(first.get(k, {}), second.get(k, {}), lambda_func)
            for k in first_set | second_set
        }

    @staticmethod
    def __map_any_leftovers(first: dict[str, int],
                            second: dict[str, int], lambda_func) -> dict[str, int]:
        first_set = set(first)
        second_set = set(second)
        return {
            k: lambda_func(first.get(k, 0), second.get(k, 0))
            for k in first_set | second_set
        }

    @staticmethod
    def __find_history_unit_to_calc(history: list[ProductHistoryUnit], from_date: datetime) -> ProductHistoryUnit:
        date_to_stop = from_date - date_root.timedelta(DAYS_IN_MONTH)
        for i in range(len(history) - 1, 0):
            if history[i].unit_date < date_to_stop:
                return history[i]
        return history[0]
