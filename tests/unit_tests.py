import unittest

import numpy as np

from jorm.market.infrastructure import Niche, MarketplaceNiche

from utils.calc_utils import get_frequency_stats
from utils.margin_calc import unit_economy_calc, unit_economy_calc_with_jorm, get_mean_concurrent_cost
from tests.test_data import cost_data
from utils.temporary import get_commission_for, WB_OWNED


class MyTestCase(unittest.TestCase):
    def test_only_freq_calc(self):
        n_samples = int(len(cost_data) * 0.1)  # todo think about number of samples
        x, y = get_frequency_stats(cost_data, n_samples + 1)
        self.assertEqual(len(x), n_samples + 1)

    def test_mean_concurrent_cost_calc(self):
        costs = np.array(cost_data.copy())
        costs.sort()
        buy = 500_00
        pack = 150_00
        unit_cost: int = buy + pack
        mid_cost = get_mean_concurrent_cost(costs, unit_cost, 0.17, 15, 5500)
        self.assertEqual(mid_cost, 971_23)

    def test_mean_concurrent_cost_calc_with_niche(self):
        niche: Niche = MarketplaceNiche("Test niche", 0.17, 5500, 0.1, [])
        niche_cost_data = cost_data.copy()
        niche_cost_data.sort()
        niche.cost_data = np.array(niche_cost_data)
        buy = 500_00
        pack = 150_00
        unit_cost: int = buy + pack
        mid_cost: int = niche.get_mean_concurrent_cost(unit_cost, 15)
        self.assertEqual(mid_cost, 971_23)

    def test_unit_economy_calc(self):
        costs = np.array(cost_data.copy())
        costs.sort()
        buy: int = 50_00
        pack: int = 50_00
        commission: float = 0.17
        logistic_to_customer: int = 55_00
        storage: int = 15
        returned_percent: float = 0.1
        client_tax: float = 0.06
        transit_price: int = 1000_00
        transit_count = 1000
        result = unit_economy_calc(buy, pack, commission, logistic_to_customer, storage,
                                   returned_percent, client_tax, costs, transit_price, transit_count)
        self.assertEqual(result["Margin"][0], 71_07)

    def test_unit_economy_calc_with_jorm(self):
        niche: Niche = MarketplaceNiche("Test niche", 0.17, 5500, 0.1, [])
        niche_cost_data = cost_data.copy()
        niche_cost_data.sort()
        niche.cost_data = np.array(niche_cost_data)
        buy: int = 50_00
        pack: int = 50_00
        storage: int = 15
        client_tax: float = 0.06
        transit_price: int = 1000_00
        transit_count = 1000
        result = unit_economy_calc_with_jorm(buy, pack, storage, client_tax, niche, transit_price, transit_count)
        self.assertEqual(result["Margin"][0], 71_07)

    def test_commission_load(self):
        commission: float = get_commission_for("Автомобильные товары", "Подстаканники электрические", WB_OWNED)
        self.assertEqual(commission, 0.17)


if __name__ == '__main__':
    unittest.main()
