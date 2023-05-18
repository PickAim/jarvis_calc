from jorm.market.infrastructure import Niche, Warehouse
from jorm.market.person import User
from jorm.support.constants import DAYS_IN_MONTH


class UnitEconomyCalculator:
    @staticmethod
    def calculate(buy_price: int,
                  pack_price: int,
                  niche: Niche,
                  warehouse: Warehouse,
                  user: User,
                  transit_price: int = 0.0,
                  transit_count: int = 0.0,
                  market_place_transit_price: int = 0.0) -> dict[str, int | float]:
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

            revenue = mean_concurrent_cost * transit_count or 1
            investments = unit_cost * transit_count
            marketplace_expenses: int = int(revenue * niche_commission + logistic_expanses
                                            + warehouse.calculate_storage_price(volume) * transit_count)
            result_transit_profit = revenue - investments - marketplace_expenses - int(
                revenue * user.get_profit_tax())

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
            "roi": result_transit_profit / investments,  # ROI
            "transit_margin": result_transit_profit / revenue,  # Маржа с транзита (%)
        }
