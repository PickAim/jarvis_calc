import datetime as date_root
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

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


class KeywordsCalculator(Calculator):
    good_match: float = 5.0
    intermediate_match: float = 2.5
    poor_match: float = 1.0

    def calculate(self, main_sentence: str, related_words: Iterable[str]):
        scored_dict: dict[float, list[str]] = self.score_object_names(main_sentence, related_words)
        result: list[str] = []
        for score in scored_dict.keys():
            result.extend(self.sort_by_len_alphabet(scored_dict[score]))
        return result

    @staticmethod
    def sort_by_len_alphabet(names: list[str]) -> list[str]:
        length_dict: dict[int, list[str]] = {}
        for name in names:
            if len(name) not in length_dict:
                length_dict[len(name)] = [name]
                continue
            length_dict[len(name)].append(name)
        sorted_tuples: list = sorted(length_dict.items())
        result: list[str] = []
        for length_tuple in sorted_tuples:
            result.extend(sorted(length_tuple[1]))
        return result

    def score_object_names(self, sentence_to_search: str, candidates: Iterable[str]) -> dict[float, list[str]]:
        sentence_to_search = sentence_to_search.lower()
        searched_words = []
        if len(sentence_to_search) > 1:
            searched_words: list[str] = sentence_to_search.split(" ")
            if len(searched_words) == 1:
                mid_idx: int = len(sentence_to_search) // 2
                searched_words = [sentence_to_search[:mid_idx], sentence_to_search[mid_idx:]]
        lower_names: list[str] = [lower_name.lower() for lower_name in candidates]
        result: dict[float, list[str]] = {
            self.good_match: [],
            self.intermediate_match: [],
            self.poor_match: []
        }
        for name in lower_names:
            words: list[str] = [word + " " for word in name.split(" ")]
            if sentence_to_search + " " in words[: len(words) // 2] \
                    or sentence_to_search + " " in words and len(words) < 3:
                result[self.good_match].append(name)
                continue
            flag: bool = False
            for word_to_match in searched_words:
                if self.any_contains(word_to_match, words):
                    result[self.intermediate_match].append(name)
                    flag = True
                    break
            if flag:
                continue
            result[self.poor_match].append(name)
        return result

    @staticmethod
    def any_contains(text_to_search: str, words: list[str]) -> bool:
        sentence: str = "".join(words)
        for word in words:
            if text_to_search in word and sentence.index(text_to_search) < len(sentence) // 2:
                return True
        return False
