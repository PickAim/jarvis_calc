from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import Client

SAMPLES_COUNT: int = 20
MONTH: int = 30


def unit_economy_calc_with_jorm(buy_price: int,
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
        result_storage_price = MONTH * result_storage_price

        volume: float = niche.get_mean_product_volume()
        logistic_expanses: int = market_place_transit_price
        if market_place_transit_price == 0:
            logistic_expanses =\
                warehouse.calculate_logistic_price_for_one(volume, niche.returned_percent) * transit_count

        revenue = mean_concurrent_cost * transit_count
        investments = unit_cost * transit_count
        marketplace_expenses: int = int(revenue * niche_commission + logistic_expanses
                                        + warehouse.calculate_storage_price(volume) * transit_count)
        result_transit_profit = revenue - investments - marketplace_expenses - int(revenue * client.get_profit_tax())

    result_product_margin: int = (mean_concurrent_cost - result_commission
                                  - result_logistic_price - result_storage_price - unit_cost)

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
