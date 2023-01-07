from jorm.market.infrastructure import Niche
from numpy import ndarray

SAMPLES_COUNT: int = 20
MONTH: int = 30


def unit_economy_calc(buy_price: int,
                      pack_price: int,
                      commission: float,
                      logistic_to_customer: int,
                      storage_price: int,
                      returned_percent: float,
                      client_tax: float,
                      cost_data: ndarray,
                      transit_price: int = 0.0,
                      transit_count: int = 0.0) -> dict:
    unit_cost: int = (buy_price + pack_price)
    mean_concurrent_cost: int = get_mean_concurrent_cost(cost_data, unit_cost, commission,
                                                         storage_price, logistic_to_customer)
    result_commission: int = int(mean_concurrent_cost * commission)
    result_logistic_price: int = logistic_to_customer
    result_storage_price = storage_price
    if transit_count > 0:
        result_logistic_price += transit_price / transit_count
        result_storage_price = MONTH * storage_price
    result_product_margin: int \
        = mean_concurrent_cost - result_commission - result_logistic_price - result_storage_price - unit_cost

    revenue: int = mean_concurrent_cost * transit_count
    investments: int = unit_cost * transit_count
    marketplace_expenses: int = int(revenue * commission
                                    + logistic_to_customer * transit_count
                                    + transit_count * returned_percent * 33)
    result_transit_profit: int = revenue - investments - marketplace_expenses - int(revenue * client_tax)
    return {
        "Pcost": (buy_price, float(buy_price) / mean_concurrent_cost),  # Закупочная себестоимость
        "Pack": (pack_price, float(pack_price) / mean_concurrent_cost),  # Упаковка
        "Mcomm": (result_commission, float(result_commission) / mean_concurrent_cost),  # Комиссия маркетплейса
        "Log": (result_logistic_price, float(result_logistic_price) / mean_concurrent_cost),  # Логистика
        "Store": (result_storage_price, float(result_storage_price) / mean_concurrent_cost),  # Хранение
        "Margin": (result_product_margin, float(result_product_margin) / mean_concurrent_cost),  # Маржа в копейках
        "TProfit": (result_transit_profit, 1.0),  # Чистая прибыль с транзита
        "ROI": (result_transit_profit / investments, 1.0),  # ROI
        "TMargin": (result_transit_profit / revenue, 1.0)  # Маржа с транзита (%)
    }


def unit_economy_calc_with_jorm(buy_price: int,
                                pack_price: int,
                                storage_price: int,
                                client_tax: float,
                                niche: Niche,
                                transit_price: int = 0.0,
                                transit_count: int = 0.0) -> dict:
    unit_cost: int = (buy_price + pack_price)
    mean_concurrent_cost: int = niche.get_mean_concurrent_cost(unit_cost, storage_price)
    result_commission: int = int(mean_concurrent_cost * niche.commission)
    result_logistic_price: int = niche.logistic_price
    result_storage_price = storage_price
    if transit_count > 0:
        result_logistic_price += transit_price / transit_count
        result_storage_price = MONTH * storage_price
    result_product_margin: int \
        = mean_concurrent_cost - result_commission - result_logistic_price - result_storage_price - unit_cost

    revenue: int = mean_concurrent_cost * transit_count
    investments: int = unit_cost * transit_count
    marketplace_expenses: int = int(revenue * niche.commission
                                    + niche.logistic_price * transit_count
                                    + transit_count * niche.returned_percent * 33)
    result_transit_profit: int = revenue - investments - marketplace_expenses - int(revenue * client_tax)
    return {
        "Pcost": (buy_price, float(buy_price) / mean_concurrent_cost),  # Закупочная себестоимость
        "Pack": (pack_price, float(pack_price) / mean_concurrent_cost),  # Упаковка
        "Mcomm": (result_commission, float(result_commission) / mean_concurrent_cost),  # Комиссия маркетплейса
        "Log": (result_logistic_price, float(result_logistic_price) / mean_concurrent_cost),  # Логистика
        "Store": (result_storage_price, float(result_storage_price) / mean_concurrent_cost),  # Хранение
        "Margin": (result_product_margin, float(result_product_margin) / mean_concurrent_cost),  # Маржа в копейках
        "TProfit": (result_transit_profit, 1.0),  # Чистая прибыль с транзита
        "ROI": (result_transit_profit / investments, 1.0),  # ROI
        "TMargin": (result_transit_profit / revenue, 1.0)  # Маржа с транзита (%)
    }


def get_concurrent_margin(mid_cost: float,
                          unit_cost: int,
                          unit_storage_cost: int,
                          commission: float,
                          logistic_price: int) -> int:
    return int(mid_cost - unit_cost - commission * mid_cost - logistic_price - unit_storage_cost)


def get_mean_concurrent_cost(cost_data: ndarray,
                             unit_cost: int,
                             commission: float,
                             storage_price: int,
                             logistic_to_customer: int) -> int:
    keys: list[int] = []
    step: int = len(cost_data) // SAMPLES_COUNT
    for i in range(SAMPLES_COUNT - 1):
        keys.append(i * step)
    keys.append(len(cost_data) - 1)
    for i in range(1, len(keys)):
        concurrent_margin: int = get_concurrent_margin(cost_data[keys[i - 1]:keys[i]].mean(), unit_cost,
                                                       storage_price, commission, logistic_to_customer)
        if concurrent_margin > 0:
            return int(cost_data[keys[i - 1]:keys[i]].mean())
    return int(cost_data[-2:-1].mean())
