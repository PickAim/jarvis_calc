import datetime

from jorm.market.items import Product


def calculate_trade_profits(products: list[Product], freq_keys: list[int],
                              from_date: datetime.datetime = datetime.datetime.utcnow()) -> list[int]:
    trade_profits: list[int] = [0 for _ in range(len(freq_keys))]
    sorted_products = sorted(products, key=lambda prod: prod.cost, reverse=True)
    j = len(freq_keys) - 1
    for i, product in enumerate(sorted_products):
        if product.cost < freq_keys[j] and j > 0:
            j -= 1
        trade_profits[j] = product.history.get_last_month_trade_count(from_date) * product.cost
    return trade_profits


def calculate_trade_frequencies(products: list[Product], freq_keys: list[int],
                                  from_date: datetime.datetime = datetime.datetime.utcnow()) -> list[int]:
    trade_frequencies: list[int] = [0 for _ in range(len(freq_keys))]
    sorted_products = sorted(products, key=lambda prod: prod.cost, reverse=True)
    j = len(freq_keys) - 1
    for i, product in enumerate(sorted_products):
        if product.cost < freq_keys[j] and j > 0:
            j -= 1
        trade_frequencies[j] = product.history.get_last_month_trade_count(from_date)
    return trade_frequencies
