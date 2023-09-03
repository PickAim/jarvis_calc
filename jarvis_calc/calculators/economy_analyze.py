import dataclasses
from dataclasses import dataclass

from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User
from jorm.support.calculation import TransitEconomyResult, SimpleEconomyResult
from jorm.support.constants import DAYS_IN_MONTH

from jarvis_calc.calculators.calculator_base import Calculator

_MAX_MASS = 25
_MAX_SIDE_SUM = 200
_MAX_SIDE_LENGTH = 120
_MAX_STANDARD_VOLUME_IN_LITERS = 5

_RETURN_PRICE = 50_00
_OVERSIZE_LOGISTIC_PRICE = 1000_00
_OVERSIZE_STORAGE_PRICE = 2_157
_STANDARD_WAREHOUSE_LOGISTIC_PRICE = 50_00
_STANDARD_WAREHOUSE_STORAGE_PRICE = 30

_NDS_TAX = 0.20
_COMMERCIAL_TAX = 0.15
_SELF_EMPLOYED_TAX = 0.06


@dataclass
class SimpleEconomyCalculateData:
    product_exist_cost: int  # user defined cost for product
    cost_price: int  # how much it cost for user
    length: int
    width: int
    height: int
    mass: int


@dataclass
class TransitEconomyCalculateData(SimpleEconomyCalculateData):
    transit_price: int
    transit_count: int


class SimpleEconomyCalculator(Calculator):

    @classmethod
    def calculate(cls, data: SimpleEconomyCalculateData,
                  niche: Niche, target_warehouse: Warehouse) -> tuple[SimpleEconomyResult, SimpleEconomyResult]:
        user_result: SimpleEconomyResult = cls.__calc_result(data, niche, target_warehouse)
        recommended_result: SimpleEconomyResult = cls.__calc_recommended_result(data, niche,
                                                                                target_warehouse)
        return user_result, recommended_result

    @classmethod
    def __calc_result(cls, data: SimpleEconomyCalculateData,
                      niche: Niche, target_warehouse: Warehouse) -> SimpleEconomyResult:
        logistic_price: int = cls.__calc_logistic_price(data, target_warehouse)
        storage_price: int = cls.__calc_storage_price(data, target_warehouse)
        purchase_cost: int = cls.__calc_purchase_cost(data)
        marketplace_expanses: int = cls.__calc_marketplace_expanses(data, niche,
                                                                    target_warehouse)
        absolute_margin: int = cls.__calc_absolute_margin(data, niche, target_warehouse)
        relative_margin: float = cls.__calc_relative_margin(data, niche, target_warehouse)
        roi: float = cls.__calc_roi(data, niche, target_warehouse)
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

    @classmethod
    def __calc_recommended_result(cls, data: SimpleEconomyCalculateData,
                                  niche: Niche, target_warehouse: Warehouse) -> SimpleEconomyResult:
        recommended_cost = cls.__get_recommended_cost(data, niche, target_warehouse)
        recommended_data = dataclasses.replace(data)
        recommended_data.product_exist_cost = recommended_cost
        return cls.__calc_result(recommended_data, niche, target_warehouse)

    @classmethod
    def __get_recommended_cost(cls, data: SimpleEconomyCalculateData,
                               niche: Niche, target_warehouse: Warehouse) -> int:
        logistic_price: int = cls.__calc_logistic_price(data, target_warehouse)
        storage_price: int = cls.__calc_storage_price(data, target_warehouse)
        mean_concurrent_cost: int = niche.get_mean_concurrent_cost(data.cost_price, logistic_price, storage_price)
        concurrent_data = dataclasses.replace(data)
        concurrent_data.product_exist_cost = mean_concurrent_cost
        concurrent_economy_result = cls.__calc_result(concurrent_data, niche, target_warehouse)
        return int(
            mean_concurrent_cost
            + concurrent_economy_result.purchase_cost
            + concurrent_economy_result.marketplace_expanses
        )

    @classmethod
    def __calc_roi(cls, data: SimpleEconomyCalculateData, niche: Niche, target_warehouse: Warehouse) -> float:
        purchase_cost: int = cls.__calc_purchase_cost(data)
        return cls.__calc_absolute_margin(data, niche, target_warehouse) / purchase_cost

    @classmethod
    def __calc_relative_margin(cls, data: SimpleEconomyCalculateData, niche: Niche,
                               target_warehouse: Warehouse) -> float:
        return cls.__calc_absolute_margin(data, niche, target_warehouse) / data.product_exist_cost

    @classmethod
    def __calc_absolute_margin(cls, data: SimpleEconomyCalculateData, niche: Niche, target_warehouse: Warehouse) -> int:
        product_cost: int = data.product_exist_cost
        purchase_cost: int = cls.__calc_purchase_cost(data)
        marketplace_expanses: int = cls.__calc_marketplace_expanses(data, niche, target_warehouse)
        return int(
            product_cost - marketplace_expanses - purchase_cost
        )

    @classmethod
    def __calc_marketplace_expanses(cls, data: SimpleEconomyCalculateData, niche: Niche,
                                    target_warehouse: Warehouse) -> int:
        product_cost = data.product_exist_cost
        niche_commission = niche.commissions[target_warehouse.handler_type]
        niche_return_percent = niche.returned_percent
        logistic_price: int = cls.__calc_logistic_price(data, target_warehouse)
        storage_price: int = cls.__calc_storage_price(data, target_warehouse)
        return int(
            niche_commission * product_cost
            + storage_price * DAYS_IN_MONTH
            + logistic_price
            + niche_return_percent * _RETURN_PRICE
        )

    @classmethod
    def __calc_purchase_cost(cls, data: SimpleEconomyCalculateData) -> int:
        cost_price = data.cost_price
        if isinstance(data, TransitEconomyCalculateData):
            transit_price = data.transit_price
            transit_count = data.transit_count
            return int(cost_price + transit_price / transit_count)
        return cost_price

    @classmethod
    def __calc_logistic_price(cls, data: SimpleEconomyCalculateData, warehouse: Warehouse) -> int:
        is_oversize: bool = cls.__is_oversize(data)
        if is_oversize:
            return _OVERSIZE_LOGISTIC_PRICE
        volume: float = cls.__calc_volume_in_liters(data)
        if volume <= _MAX_STANDARD_VOLUME_IN_LITERS:
            return int(warehouse.main_coefficient * _STANDARD_WAREHOUSE_LOGISTIC_PRICE)
        over_standard_volume = volume - _MAX_STANDARD_VOLUME_IN_LITERS
        return int(
            warehouse.main_coefficient * (_STANDARD_WAREHOUSE_LOGISTIC_PRICE +
                                          over_standard_volume * _STANDARD_WAREHOUSE_LOGISTIC_PRICE / 10)
        )

    @classmethod
    def __calc_storage_price(cls, data: SimpleEconomyCalculateData, warehouse: Warehouse) -> int:
        is_oversize: bool = cls.__is_oversize(data)
        if is_oversize:
            return _OVERSIZE_STORAGE_PRICE
        volume: float = cls.__calc_volume_in_liters(data)
        if volume <= _MAX_STANDARD_VOLUME_IN_LITERS:
            return int(warehouse.main_coefficient * _STANDARD_WAREHOUSE_STORAGE_PRICE)
        over_standard_volume = volume - _MAX_STANDARD_VOLUME_IN_LITERS
        return int(
            warehouse.main_coefficient * (_STANDARD_WAREHOUSE_STORAGE_PRICE +
                                          over_standard_volume * _STANDARD_WAREHOUSE_STORAGE_PRICE / 10)
        )

    @classmethod
    def __is_oversize(cls, data: SimpleEconomyCalculateData) -> bool:
        mass: int = data.mass
        if mass > _MAX_MASS:
            return True
        if data.length + data.width + data.height > _MAX_SIDE_SUM:
            return True
        return data.length > _MAX_SIDE_LENGTH or data.width > _MAX_SIDE_LENGTH or data.height > _MAX_SIDE_LENGTH

    @classmethod
    def __calc_volume_in_liters(cls, data: SimpleEconomyCalculateData) -> float:
        return data.length * data.width * data.height * 0.001


class TransitEconomyCalculator(Calculator):
    @classmethod
    def calculate(cls, data: TransitEconomyCalculateData, niche: Niche,
                  user: User, target_warehouse: Warehouse) -> tuple[TransitEconomyResult, TransitEconomyResult]:
        user_result, recommended_result = SimpleEconomyCalculator.calculate(data, niche, target_warehouse)
        user_transit_result = cls.__calc_transit_result(user_result, data, user)
        recommended_transit_result = cls.__calc_transit_result(recommended_result, data, user)
        return user_transit_result, recommended_transit_result

    @classmethod
    def __calc_transit_result(cls, simple_result: SimpleEconomyResult,
                              data: TransitEconomyCalculateData, user: User) -> TransitEconomyResult:
        purchase_investments: int = cls.__calc_purchase_investments(simple_result, data)
        commercial_expanses: int = cls.__calc_commercial_expanses(simple_result, data)
        tax_expanses: int = cls.__calc_tax_expanses(simple_result, data, user)
        absolute_transit_margin: int = cls.__calc_absolute_transit_margin(simple_result,
                                                                          data, user)
        relative_transit_margin: float = cls.__calc_relative_transit_margin(simple_result,
                                                                            data, user)
        transit_roi: float = cls.__calc_transit_roi(simple_result, data, user)
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

    @classmethod
    def __calc_transit_roi(cls, simple_result: SimpleEconomyResult,
                           data: TransitEconomyCalculateData, user: User) -> float:
        purchase_investments: int = cls.__calc_purchase_investments(simple_result, data)
        absolute_transit_margin: int = cls.__calc_absolute_transit_margin(simple_result,
                                                                          data, user)
        return absolute_transit_margin / purchase_investments

    @classmethod
    def __calc_relative_transit_margin(cls, simple_result: SimpleEconomyResult,
                                       data: TransitEconomyCalculateData, user: User) -> float:
        return (cls.__calc_absolute_transit_margin(simple_result, data, user)
                / (simple_result.result_cost * data.transit_count))

    @classmethod
    def __calc_absolute_transit_margin(cls, simple_result: SimpleEconomyResult,
                                       data: TransitEconomyCalculateData, user: User) -> int:
        tax_expanses = cls.__calc_tax_expanses(simple_result, data, user)
        clear_profit = cls.__calc_clear_profit(simple_result, data)
        return int(clear_profit - tax_expanses)

    @classmethod
    def __calc_tax_expanses(cls, simple_result: SimpleEconomyResult, data: TransitEconomyCalculateData, user: User):
        return int(
            user.profit_tax * cls.__calc_taxed_sum(simple_result, data, user)
        )

    @classmethod
    def __calc_taxed_sum(cls, simple_result: SimpleEconomyResult, data: TransitEconomyCalculateData, user: User) -> int:
        if user.profit_tax <= _SELF_EMPLOYED_TAX:
            return int(
                simple_result.result_cost * data.transit_count
            )
        return cls.__calc_clear_profit(simple_result, data)

    @classmethod
    def __calc_clear_profit(cls, simple_result: SimpleEconomyResult, data: TransitEconomyCalculateData) -> int:
        purchase_investments = cls.__calc_purchase_investments(simple_result, data)
        commercial_expanses = cls.__calc_commercial_expanses(simple_result, data)
        expanses = purchase_investments + commercial_expanses
        return int(
            simple_result.result_cost * data.transit_count - expanses
        )

    @classmethod
    def __calc_commercial_expanses(cls, simple_result: SimpleEconomyResult, data: TransitEconomyCalculateData) -> int:
        return int(
            data.transit_count * simple_result.marketplace_expanses
        )

    @classmethod
    def __calc_purchase_investments(cls, simple_result: SimpleEconomyResult, data: TransitEconomyCalculateData) -> int:
        return int(
            data.transit_count * simple_result.purchase_cost
        )
