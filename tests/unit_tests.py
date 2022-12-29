import unittest

import numpy as np

from utils.calc_utils import get_frequency_stats
from utils.margin_calc import unit_economy_calc, get_mean_concurrent_cost
from tests.test_data import cost_data


class MyTestCase(unittest.TestCase):
    def test_only_freq_calc(self):
        n_samples = int(len(cost_data) * 0.1)  # todo think about number of samples
        x, y = get_frequency_stats(cost_data, n_samples + 1)
        self.assertEqual(len(x), n_samples + 1)

    def test_unit_economy_calc(self):
        costs = np.array(cost_data.copy())
        costs.sort()
        buy = 500
        pack = 150
        transit = 0
        unit_count = 0
        mid_cost = get_mean_concurrent_cost(costs, buy, pack, 20)
        result_dict = unit_economy_calc(buy, pack, mid_cost, transit, unit_count)
        self.assertTrue(result_dict)


if __name__ == '__main__':
    unittest.main()
