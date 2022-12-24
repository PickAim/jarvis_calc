import numpy as np

# now it's just constants
commission: float = 0.1
logistic_price: int = 55
storage_price: float = 0.04
wrep: int = 45


def unit_economy_calc(buy_price: int, pack_price: int, mid_cost: int, transit_price: int = 0.0,
                      unit_count: int = 0.0) -> dict[str: tuple[int, float]]:
    unit_cost: int = buy_price + pack_price
    unit_storage_cost: int = int(wrep * storage_price)

    partial_unit_cost: int = int((unit_cost + logistic_price + unit_storage_cost) * (1 + commission))
    partial_unit_transit_cost: int = 0
    if unit_count > 0:
        partial_unit_transit_cost = int(partial_unit_cost + (float(transit_price) / unit_count) * (1 + commission))

    margin: int = int((1 - commission) * mid_cost - partial_unit_cost)

    transit_margin: int = 0
    if unit_count > 0:
        transit_margin = int((1 - commission) * mid_cost - partial_unit_transit_cost)

    partial_cost: int = unit_cost + logistic_price + unit_storage_cost
    if margin > 0:
        partial_cost += margin
    cost: int = int((1 + commission) * partial_cost)

    transit_cost: int = 0
    if unit_count > 0:
        transit_cost = cost + int((float(transit_price) / unit_count) * (1 + commission))

    full_commission: int = int(commission * partial_cost)
    old_margin = margin
    if margin > 0:
        margin = int(margin * (1 - commission))
    else:
        margin = int(margin * (1 + commission))
    result = {
        "Pcost": (buy_price, float(buy_price) / (cost - commission * old_margin)),  # Закупочная себестоимость
        "Pack": (pack_price, float(pack_price) / (cost - commission * old_margin)),  # Упаковка
        "Mcomm": (full_commission, float(full_commission) / (cost - commission * old_margin)),  # Комиссия маркетплейса
        "Log": (logistic_price, float(logistic_price) / (cost - commission * old_margin)),  # Логистика
        "Store": (unit_storage_cost, float(unit_storage_cost) / (cost - commission * old_margin)),  # Хранение
        "Margin": (margin, float(abs(margin)) / (cost - commission * old_margin)),  # Маржа
    }
    if margin > 0:
        result["Price"] = (cost, float(unit_cost) / (cost - commission * old_margin) * 100
                           + float(full_commission) / (cost - commission * old_margin) * 100
                           + float(logistic_price) / (cost - commission * old_margin) * 100
                           + float(unit_storage_cost) / (cost - commission * old_margin) * 100
                           + float(margin) / (cost - commission * old_margin) * 100)  # Цена
    else:
        result["Price"] = (cost, float(unit_cost) / cost * 100
                           + float(full_commission) / cost * 100
                           + float(logistic_price) / cost * 100
                           + float(unit_storage_cost) / cost * 100)  # Цена
    result["Commis"] = (0, cost * commission)
    if unit_count > 0:
        result["tr_margin"] = (0, transit_margin)
        result["tr_cost"] = (0, transit_cost)
        result["tr_delta"] = (0, transit_cost - cost)
    return result


def get_concurrent_margin(mid_cost, unit_cost, unit_storage_cost):
    return mid_cost - unit_cost - commission * mid_cost - logistic_price - unit_storage_cost


def get_mean_concurrent_cost(cost_data: np.array, buy_price, pack_price, n_samples) -> int:
    unit_cost = (buy_price + pack_price) * 100
    unit_storage_cost = (wrep * storage_price) * 100
    keys = []
    step = len(cost_data) // n_samples
    for i in range(n_samples - 1):
        keys.append(i * step)
    keys.append(len(cost_data) - 1)
    for i in range(1, len(keys)):
        concurrent_margin = get_concurrent_margin(cost_data[keys[i-1]:keys[i]].mean(), unit_cost, unit_storage_cost)
        if concurrent_margin > 0:
            return cost_data[keys[i-1]:keys[i]].mean() / 100
    return int(cost_data[-2:-1].mean() / 100)

