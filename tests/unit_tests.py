import time
import unittest
from os.path import join

import numpy as np
import constants

from calc_utils import get_frequency_stats
from jarvis_utils import load_data
from load_data import load
from load_storage import get_storage_data
from margin_calc import unit_economy_calc, get_mean_concurrent_cost
from tests.test_data import cost_data


class MyTestCase(unittest.TestCase):
    def test_only_freq_calc(self):
        n_samples = int(len(cost_data) * 0.1)  # todo think about number of samples
        x, y = get_frequency_stats(cost_data, n_samples + 1)
        self.assertEqual(len(x), n_samples + 1)

    def test_load_storage(self):
        product_ids = [26414401, 6170053]
        storage_data: dict[int, dict[int, int]] = get_storage_data(product_ids)
        self.assertIsNotNone(storage_data)
        self.assertEqual(2, len(storage_data.keys()))

    def test_unit_economy_calc(self):
        niche = 'кофе'
        is_update = False
        pages_num = 1
        load(niche, constants.data_path, is_update, pages_num)
        filename = str(join(constants.data_path, niche + ".txt"))
        costs = np.array(load_data(filename))
        costs.sort()
        buy = 500
        pack = 150
        transit = 0
        unit_count = 0
        mid_cost = get_mean_concurrent_cost(costs, buy, pack, 20)
        result_dict = unit_economy_calc(buy, pack, mid_cost, transit, unit_count)
        self.assertTrue(result_dict)

    def test_load_n_freq_calc(self):
        text_to_search = 'молотый кофе'
        is_update = True
        pages_num = 1
        start_time = time.time()
        load(text_to_search, constants.data_path, is_update, pages_num)
        print(time.time() - start_time)
        filename = str(join(constants.data_path, text_to_search + ".txt"))
        loaded_cost_data = load_data(filename)
        n_samples = int(len(loaded_cost_data) * 0.1)  # todo think about number of samples
        x, y = get_frequency_stats(loaded_cost_data, n_samples + 1)
        self.assertEqual(len(x), n_samples + 1)


if __name__ == '__main__':
    unittest.main()
