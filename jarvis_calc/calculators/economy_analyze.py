import dataclasses
from dataclasses import dataclass

from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User
from jorm.support.calculation import TransitEconomyResult, SimpleEconomyResult, GreenTradeZoneCalculateResult
from jorm.support.constants import DAYS_IN_MONTH
from jorm.support.types import EconomyConstants

from jarvis_calc.calculators.calculator_base import Calculator


@dataclass
class SimpleEconomyCalculateData:
    product_exist_cost: int  # user defined cost for product
    cost_price: int  # how much it cost for user
    length: float
    width: float
    height: float
    mass: float


@dataclass
class TransitEconomyCalculateData(SimpleEconomyCalculateData):
    logistic_price: int
    logistic_count: int
    transit_cost_for_cubic_meter: float


class SimpleEconomyCalculator(Calculator):
    def __init__(self, economy_constants: EconomyConstants):
        self.economy_constants: EconomyConstants = economy_constants

    def calculate(self, data: SimpleEconomyCalculateData,
                  niche: Niche, target_warehouse: Warehouse,
                  green_zone_result: GreenTradeZoneCalculateResult) -> tuple[SimpleEconomyResult, SimpleEconomyResult]:
        user_result: SimpleEconomyResult = self.__calc_result(data, niche, target_warehouse)
        recommended_result: SimpleEconomyResult = self.__calc_recommended_result(data, niche,
                                                                                 target_warehouse, green_zone_result)
        return user_result, recommended_result

    def __calc_result(self, data: SimpleEconomyCalculateData,
                      niche: Niche, target_warehouse: Warehouse) -> SimpleEconomyResult:
        logistic_price: int = self.__calc_logistic_price(data, target_warehouse)
        storage_price: int = self.__calc_storage_price(data, target_warehouse)
        purchase_cost: int = self.__calc_purchase_cost(data)
        marketplace_expanses: int = self.__calc_marketplace_expanses(data, niche,
                                                                     target_warehouse)
        absolute_margin: int = self.__calc_absolute_margin(data, niche, target_warehouse)
        relative_margin: float = self.__calc_relative_margin(data, niche, target_warehouse)
        roi: float = self.__calc_roi(data, niche, target_warehouse)
        return SimpleEconomyResult(
            result_cost=data.product_exist_cost,
            logistic_price=logistic_price,
            storage_price=storage_price,
            purchase_cost=purchase_cost,
            marketplace_expanses=marketplace_expanses,
            absolute_margin=absolute_margin,
            relative_margin=relative_margin,
            roi=roi
        )

    def __calc_recommended_result(self, data: SimpleEconomyCalculateData,
                                  niche: Niche, target_warehouse: Warehouse,
                                  green_zone_result: GreenTradeZoneCalculateResult) -> SimpleEconomyResult:
        recommended_cost = self.__get_recommended_cost(green_zone_result)
        recommended_data = dataclasses.replace(data)
        recommended_data.product_exist_cost = recommended_cost
        return self.__calc_result(recommended_data, niche, target_warehouse)

    @staticmethod
    def __get_recommended_cost(green_zone_result: GreenTradeZoneCalculateResult) -> int:
        best_segment = green_zone_result.segments[green_zone_result.best_segment_idx]
        return int(sum(best_segment) / len(best_segment))

    def __calc_roi(self, data: SimpleEconomyCalculateData, niche: Niche, target_warehouse: Warehouse) -> float:
        purchase_cost: int = self.__calc_purchase_cost(data)
        return self.__calc_absolute_margin(data, niche, target_warehouse) / purchase_cost

    def __calc_relative_margin(self, data: SimpleEconomyCalculateData, niche: Niche,
                               target_warehouse: Warehouse) -> float:
        return self.__calc_absolute_margin(data, niche, target_warehouse) / data.product_exist_cost

    def __calc_absolute_margin(self, data: SimpleEconomyCalculateData, niche: Niche,
                               target_warehouse: Warehouse) -> int:
        product_cost: int = data.product_exist_cost
        purchase_cost: int = self.__calc_purchase_cost(data)
        marketplace_expanses: int = self.__calc_marketplace_expanses(data, niche, target_warehouse)
        return int(
            product_cost - marketplace_expanses - purchase_cost
        )

    def __calc_marketplace_expanses(self, data: SimpleEconomyCalculateData, niche: Niche,
                                    target_warehouse: Warehouse) -> int:
        product_cost = data.product_exist_cost
        niche_commission = target_warehouse.get_niche_commission(niche)
        niche_return_percent = niche.returned_percent
        logistic_price: int = self.__calc_logistic_price(data, target_warehouse)
        storage_price: int = self.__calc_storage_price(data, target_warehouse)
        return int(
            niche_commission * product_cost
            + storage_price * DAYS_IN_MONTH
            + logistic_price
            + niche_return_percent * self.economy_constants.return_price
        )

    @staticmethod
    def __calc_purchase_cost(data: SimpleEconomyCalculateData) -> int:
        cost_price = data.cost_price
        if isinstance(data, TransitEconomyCalculateData):
            transit_price = data.logistic_price
            transit_count = data.logistic_count
            return int(cost_price + transit_price / transit_count)
        return cost_price

    def __calc_logistic_price(self, data: SimpleEconomyCalculateData, warehouse: Warehouse) -> int:
        is_oversize: bool = self.__is_oversize(data)
        if is_oversize:
            return self.economy_constants.oversize_logistic_price
        volume: float = self.__calc_volume_in_liters(data)
        if volume <= self.economy_constants.max_standard_volume_in_liters:
            return int(warehouse.main_coefficient * self.economy_constants.standard_warehouse_logistic_price)
        over_standard_volume = volume - self.economy_constants.max_standard_volume_in_liters
        return int(
            warehouse.main_coefficient
            * (self.economy_constants.standard_warehouse_logistic_price
               + over_standard_volume * self.economy_constants.standard_warehouse_logistic_price / 10)
        )

    def __calc_storage_price(self, data: SimpleEconomyCalculateData, warehouse: Warehouse) -> int:
        is_oversize: bool = self.__is_oversize(data)
        if is_oversize:
            return self.economy_constants.oversize_storage_price
        volume: float = self.__calc_volume_in_liters(data)
        if volume <= self.economy_constants.max_standard_volume_in_liters:
            return int(warehouse.main_coefficient * self.economy_constants.standard_warehouse_storage_price)
        over_standard_volume = volume - self.economy_constants.max_standard_volume_in_liters
        return int(
            warehouse.main_coefficient
            * (self.economy_constants.standard_warehouse_storage_price
               + over_standard_volume * self.economy_constants.standard_warehouse_storage_price / 10)
        )

    def __is_oversize(self, data: SimpleEconomyCalculateData) -> bool:
        mass: float = data.mass
        if mass > self.economy_constants.max_mass:
            return True
        if data.length + data.width + data.height > self.economy_constants.max_side_sum:
            return True
        return (data.length > self.economy_constants.max_side_length
                or data.width > self.economy_constants.max_side_length
                or data.height > self.economy_constants.max_side_length)

    @staticmethod
    def __calc_volume_in_liters(data: SimpleEconomyCalculateData) -> float:
        return data.length * data.width * data.height * 0.001


class TransitEconomyCalculator(Calculator):
    def __init__(self, economy_constants: EconomyConstants):
        self.economy_constants: EconomyConstants = economy_constants

    def calculate(self, data: TransitEconomyCalculateData, niche: Niche,
                  user: User, target_warehouse: Warehouse, green_zone_result: GreenTradeZoneCalculateResult) \
            -> tuple[TransitEconomyResult, TransitEconomyResult]:
        user_result, recommended_result = SimpleEconomyCalculator(self.economy_constants).calculate(data, niche,
                                                                                                    target_warehouse,
                                                                                                    green_zone_result)
        user_transit_result = self.__calc_transit_result(user_result, data, user)
        recommended_transit_result = self.__calc_transit_result(recommended_result, data, user)
        return user_transit_result, recommended_transit_result

    def __calc_transit_result(self, simple_result: SimpleEconomyResult,
                              data: TransitEconomyCalculateData, user: User) -> TransitEconomyResult:
        purchase_investments: int = self.__calc_purchase_investments(simple_result, data)
        commercial_expanses: int = self.__calc_commercial_expanses(simple_result, data)
        tax_expanses: int = self.__calc_tax_expanses(simple_result, data, user)
        absolute_transit_margin: int = self.__calc_absolute_transit_margin(simple_result,
                                                                           data, user)
        relative_transit_margin: float = self.__calc_relative_transit_margin(simple_result,
                                                                             data, user)
        transit_roi: float = self.__calc_transit_roi(simple_result, data, user)
        return TransitEconomyResult(
            result_cost=simple_result.result_cost,
            logistic_price=simple_result.logistic_price,
            storage_price=simple_result.storage_price,
            purchase_cost=simple_result.purchase_cost,
            marketplace_expanses=simple_result.marketplace_expanses,
            absolute_margin=simple_result.absolute_margin,
            relative_margin=simple_result.relative_margin,
            roi=simple_result.roi,

            purchase_investments=purchase_investments,
            commercial_expanses=commercial_expanses,
            tax_expanses=tax_expanses,
            absolute_transit_margin=absolute_transit_margin,
            relative_transit_margin=relative_transit_margin,
            transit_roi=transit_roi
        )

    def __calc_transit_roi(self, simple_result: SimpleEconomyResult,
                           data: TransitEconomyCalculateData, user: User) -> float:
        purchase_investments: int = self.__calc_purchase_investments(simple_result, data)
        absolute_transit_margin: int = self.__calc_absolute_transit_margin(simple_result,
                                                                           data, user)
        return absolute_transit_margin / purchase_investments

    def __calc_relative_transit_margin(self, simple_result: SimpleEconomyResult,
                                       data: TransitEconomyCalculateData, user: User) -> float:
        return (self.__calc_absolute_transit_margin(simple_result, data, user)
                / (simple_result.result_cost * data.logistic_count))

    def __calc_absolute_transit_margin(self, simple_result: SimpleEconomyResult,
                                       data: TransitEconomyCalculateData, user: User) -> int:
        tax_expanses = self.__calc_tax_expanses(simple_result, data, user)
        clear_profit = self.__calc_clear_profit(simple_result, data)
        return int(clear_profit - tax_expanses)

    def __calc_tax_expanses(self, simple_result: SimpleEconomyResult, data: TransitEconomyCalculateData, user: User):
        return int(
            user.profit_tax * self.__calc_taxed_sum(simple_result, data, user)
        )

    def __calc_taxed_sum(self, simple_result: SimpleEconomyResult, data: TransitEconomyCalculateData,
                         user: User) -> int:
        if user.profit_tax <= self.economy_constants.self_employed_tax:
            return int(
                simple_result.result_cost * data.logistic_count
            )
        return self.__calc_clear_profit(simple_result, data)

    def __calc_clear_profit(self, simple_result: SimpleEconomyResult, data: TransitEconomyCalculateData) -> int:
        purchase_investments = self.__calc_purchase_investments(simple_result, data)
        commercial_expanses = self.__calc_commercial_expanses(simple_result, data)
        expanses = purchase_investments + commercial_expanses
        return int(
            simple_result.result_cost * data.logistic_count - expanses
        )

    @staticmethod
    def __calc_commercial_expanses(simple_result: SimpleEconomyResult, data: TransitEconomyCalculateData) -> int:
        return int(
            data.logistic_count * simple_result.marketplace_expanses
        )

    @staticmethod
    def __calc_purchase_investments(simple_result: SimpleEconomyResult, data: TransitEconomyCalculateData) -> int:
        return int(
            data.logistic_count * simple_result.purchase_cost
        )
