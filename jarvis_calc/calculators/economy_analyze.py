import dataclasses
from dataclasses import dataclass

from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User
from jorm.support.constants import DAYS_IN_MONTH

from jarvis_calc.calculators.calculator_base import Calculator

_MAX_MASS = 25
_MAX_SIDE_SUM = 200
_MAX_SIDE_LENGTH = 120
_MAX_STANDARD_VOLUME_IN_LITERS = 5

_RETURN_PRICE = 50_00
_OVERSIZE_LOGISTIC_PRICE = 1000_00
_OVERSIZE_STORAGE_PRICE = 2_157
_ADDITIONAL_WAREHOUSE_LOGISTIC_PRICE = 5_00
_ADDITIONAL_WAREHOUSE_STORAGE_PRICE = 30
_STANDARD_WAREHOUSE_ACTIONS_PRICE = 50_00


@dataclass
class SimpleEconomyCalculateData:
    product_exist_cost: int
    cost_price: int
    length: int
    width: int
    height: int
    mass: int


class TransitEconomyCalculateData(SimpleEconomyCalculateData):
    transit_price: int
    transit_count: int


@dataclass
class SimpleEconomyResult:
    logistic_price: int
    storage_price: int
    purchase_cost: int
    marketplace_expanses: int
    absolute_margin: int
    relative_margin: float
    roi: float


class SimpleEconomyCalculator(Calculator):

    @staticmethod
    def calculate(data: SimpleEconomyCalculateData,
                  niche: Niche,
                  target_warehouse: Warehouse) -> tuple[SimpleEconomyResult, SimpleEconomyResult]:
        user_result: SimpleEconomyResult = SimpleEconomyCalculator._calc_result(data, niche, target_warehouse)
        recommended_result: SimpleEconomyResult = SimpleEconomyCalculator._calc_recommended_result(data, niche,
                                                                                                   target_warehouse)
        return user_result, recommended_result

    @staticmethod
    def _calc_recommended_result(data: SimpleEconomyCalculateData,
                                 niche: Niche, target_warehouse: Warehouse) -> SimpleEconomyResult:
        recommended_cost = SimpleEconomyCalculator.__get_recommended_cost(data, niche, target_warehouse)
        recommended_data = dataclasses.replace(data)
        recommended_data.product_exist_cost = recommended_cost
        return SimpleEconomyCalculator._calc_result(recommended_data, niche, target_warehouse)

    @staticmethod
    def _calc_result(data: SimpleEconomyCalculateData,
                     niche: Niche, target_warehouse: Warehouse) -> SimpleEconomyResult:
        logistic_price: int = SimpleEconomyCalculator.__calc_logistic_price(data, target_warehouse)  # result
        storage_price: int = SimpleEconomyCalculator.__calc_storage_price(data, target_warehouse)  # result
        purchase_cost: int = SimpleEconomyCalculator.__calc_purchase_cost(data)  # result
        marketplace_expanses: int = SimpleEconomyCalculator.__calc_marketplace_expanses(data, niche,
                                                                                        target_warehouse)  # result
        absolute_margin: int = SimpleEconomyCalculator.__calc_absolute_margin(data, niche, target_warehouse)  # result
        relative_margin: float = SimpleEconomyCalculator.__calc_relative_margin(data, niche, target_warehouse)  # result
        roi: float = SimpleEconomyCalculator.__calc_roi(data, niche, target_warehouse)  # result
        return SimpleEconomyResult(
            logistic_price=logistic_price,
            storage_price=storage_price,
            purchase_cost=purchase_cost,
            marketplace_expanses=marketplace_expanses,
            absolute_margin=absolute_margin,
            relative_margin=relative_margin,
            roi=roi
        )

    @staticmethod
    def __get_recommended_cost(data: SimpleEconomyCalculateData,
                               niche: Niche, target_warehouse: Warehouse) -> int:
        logistic_price: int = SimpleEconomyCalculator.__calc_logistic_price(data, target_warehouse)
        storage_price: int = SimpleEconomyCalculator.__calc_storage_price(data, target_warehouse)
        mean_concurrent_cost: int = niche.get_mean_concurrent_cost(data.cost_price, logistic_price, storage_price)
        concurrent_data = dataclasses.replace(data)
        concurrent_data.product_exist_cost = mean_concurrent_cost
        concurrent_economy_result = SimpleEconomyCalculator._calc_result(data, niche, target_warehouse)
        return int(
            mean_concurrent_cost
            + concurrent_economy_result.purchase_cost
            + concurrent_economy_result.marketplace_expanses
        )

    @staticmethod
    def __calc_roi(data: SimpleEconomyCalculateData, niche: Niche, target_warehouse: Warehouse) -> float:
        purchase_cost: int = SimpleEconomyCalculator.__calc_purchase_cost(data)
        return SimpleEconomyCalculator.__calc_absolute_margin(data, niche, target_warehouse) / purchase_cost

    @staticmethod
    def __calc_relative_margin(data: SimpleEconomyCalculateData, niche: Niche, target_warehouse: Warehouse) -> float:
        return SimpleEconomyCalculator.__calc_absolute_margin(data, niche, target_warehouse) / data.product_exist_cost

    @staticmethod
    def __calc_absolute_margin(data: SimpleEconomyCalculateData, niche: Niche, target_warehouse: Warehouse) -> int:
        product_cost: int = data.product_exist_cost
        purchase_cost: int = SimpleEconomyCalculator.__calc_purchase_cost(data)
        marketplace_expanses: int = SimpleEconomyCalculator.__calc_marketplace_expanses(data, niche, target_warehouse)
        return int(
            product_cost - marketplace_expanses - purchase_cost
        )

    @staticmethod
    def __calc_marketplace_expanses(data: SimpleEconomyCalculateData, niche: Niche, target_warehouse: Warehouse) -> int:
        product_cost = data.product_exist_cost
        niche_commission = niche.commissions[target_warehouse.handler_type]
        niche_return_percent = niche.returned_percent
        logistic_price: int = SimpleEconomyCalculator.__calc_logistic_price(data, target_warehouse)  # result
        storage_price: int = SimpleEconomyCalculator.__calc_storage_price(data, target_warehouse)  # result
        return int(
            niche_commission * product_cost
            + storage_price * DAYS_IN_MONTH
            + logistic_price
            + niche_return_percent * _RETURN_PRICE
        )

    @staticmethod
    def __calc_purchase_cost(data: SimpleEconomyCalculateData) -> int:
        cost_price = data.cost_price
        if isinstance(data, TransitEconomyCalculateData):
            transit_price = data.transit_price
            transit_count = data.transit_count
            return int(cost_price + transit_price / transit_count)
        return cost_price

    @staticmethod
    def __calc_logistic_price(data: SimpleEconomyCalculateData, warehouse: Warehouse) -> int:
        is_oversize: bool = SimpleEconomyCalculator.__is_oversize(data)
        if is_oversize:
            return _OVERSIZE_LOGISTIC_PRICE
        volume: float = SimpleEconomyCalculator.__calc_volume_in_liters(data)
        if volume <= _MAX_STANDARD_VOLUME_IN_LITERS:
            return warehouse.main_coefficient * _STANDARD_WAREHOUSE_ACTIONS_PRICE
        over_standard_volume = volume - _MAX_STANDARD_VOLUME_IN_LITERS
        return int(
            warehouse.main_coefficient * (_STANDARD_WAREHOUSE_ACTIONS_PRICE +
                                          over_standard_volume * _ADDITIONAL_WAREHOUSE_LOGISTIC_PRICE)
        )

    @staticmethod
    def __calc_storage_price(data: SimpleEconomyCalculateData, warehouse: Warehouse) -> int:
        is_oversize: bool = SimpleEconomyCalculator.__is_oversize(data)
        if is_oversize:
            return _OVERSIZE_STORAGE_PRICE
        volume: float = SimpleEconomyCalculator.__calc_volume_in_liters(data)
        if volume <= _MAX_STANDARD_VOLUME_IN_LITERS:
            return warehouse.main_coefficient * _STANDARD_WAREHOUSE_ACTIONS_PRICE
        over_standard_volume = volume - _MAX_STANDARD_VOLUME_IN_LITERS
        return int(
            warehouse.main_coefficient * (_STANDARD_WAREHOUSE_ACTIONS_PRICE +
                                          over_standard_volume * _ADDITIONAL_WAREHOUSE_STORAGE_PRICE)
        )

    @staticmethod
    def __is_oversize(data: SimpleEconomyCalculateData) -> bool:
        mass: int = data.mass
        if mass > _MAX_MASS:
            return True
        if data.length + data.width + data.height > _MAX_SIDE_SUM:
            return True
        return data.length > _MAX_SIDE_LENGTH or data.width > _MAX_SIDE_LENGTH or data.height > _MAX_SIDE_LENGTH

    @staticmethod
    def __calc_volume_in_liters(data: SimpleEconomyCalculateData) -> float:
        return data.length * data.width * data.height * 0.001
