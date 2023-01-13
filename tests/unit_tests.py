import unittest

import numpy as np

from jorm.market.infrastructure import Niche, Warehouse, Address, HandlerType
from jorm.market.items import ProductHistory, Product
from jorm.market.person import Client, ClientInfo

from jarvis_calc.utils.calc_utils import get_frequency_stats, get_frequency_stats_with_jorm
from jarvis_calc.utils.margin_calc import unit_economy_calc, unit_economy_calc_with_jorm, get_mean_concurrent_cost
from jarvis_calc.utils.temporary import get_commission_for

from tests.test_data import cost_data


class MyTestCase(unittest.TestCase):
    def test_only_freq_calc(self):
        n_samples = int(len(cost_data) * 0.1)  # todo think about number of samples
        x, y = get_frequency_stats(cost_data, n_samples)
        self.assertEqual(n_samples, len(x))

    def test_only_freq_calc_with_jorm(self):
        niche: Niche = self.create_test_niche()
        x, y = get_frequency_stats_with_jorm(niche)
        self.assertEqual(int(len(cost_data) * 0.1), len(x))

    def test_mean_concurrent_cost_calc(self):
        costs = np.array(cost_data.copy())
        costs.sort()
        buy = 500_00
        pack = 150_00
        unit_cost: int = buy + pack
        mid_cost = get_mean_concurrent_cost(costs, unit_cost, 0.17, 15, 5500)
        self.assertEqual(971_23, mid_cost)

    def test_mean_concurrent_cost_calc_with_niche(self):
        niche: Niche = self.create_test_niche()
        buy = 500_00
        pack = 150_00
        unit_cost: int = buy + pack
        mid_cost: int = niche.get_mean_concurrent_cost(unit_cost, 5500, 15)
        self.assertEqual(971_23, mid_cost)

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
        self.assertEqual(71_07, result["Margin"][0])

    def test_unit_economy_calc_with_jorm(self):
        niche: Niche = self.create_test_niche()
        buy: int = 50_00
        pack: int = 50_00
        transit_price: int = 1000_00
        transit_count = 1000
        warehouse = Warehouse("warehouse", 1, HandlerType.MARKETPLACE, Address(), [],
                              basic_logistic_to_customer_commission=5500, additional_logistic_to_customer_commission=0,
                              logistic_from_customer_commission=3300, basic_storage_commission=15,
                              additional_storage_commission=0, mono_palette_storage_commission=10)
        client = Client("client", ClientInfo(profit_tax=0.06))
        result = unit_economy_calc_with_jorm(buy, pack, niche, warehouse, client, transit_price, transit_count)
        self.assertEqual(71_07, result["Margin"][0])

    def test_commission_load(self):
        commission: float = get_commission_for("Автомобильные товары",
                                               "Подстаканники электрические", HandlerType.MARKETPLACE.__str__())
        self.assertEqual(0.17, commission)

    @staticmethod
    def create_test_niche() -> Niche:
        niche_commissions_dict: dict[HandlerType, float] = {
            HandlerType.MARKETPLACE: 0.17,
            HandlerType.PARTIAL_CLIENT: 0.15,
            HandlerType.CLIENT: 0.10
        }
        niche: Niche = Niche("Test niche", niche_commissions_dict, 0.1,
                             [Product("prod1", 15, 1, ProductHistory(),
                                      width=0.15, height=0.3, depth=0.1)])
        niche_cost_data = cost_data.copy()
        niche_cost_data.sort()
        niche.cost_data = np.array(niche_cost_data)
        return niche


if __name__ == '__main__':
    unittest.main()
