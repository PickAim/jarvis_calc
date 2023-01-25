import numpy as np
from jorm.market.infrastructure import Niche
from numpy import ndarray


def frequency_calc(costs: list[float], n_samples: int) -> tuple[list[float], list[int]]:
    res = np.histogram(costs, n_samples)
    return list(res[1][1:]), list(res[0])


def frequency_calc_new(costs: ndarray[float], n_samples: int) -> tuple[list[float], list[int]]:
    res = np.histogram(costs, n_samples)
    return list(res[1][1:]), list(res[0])


def get_cleared_mean(lst: list[int]) -> int:
    result: int = 0
    clear_frequency = np.array([x for x in lst if x != 0])
    for freq in clear_frequency:
        result += freq
    return int(result / len(clear_frequency))


def get_frequency_stats(cost_data: list[float], n_samples: int) -> tuple[list[float], list[int]]:
    # TODO remove it after DB full implements
    if len(cost_data) <= 0:
        return [], []
    cost_data.sort()
    base_keys, base_frequencies = frequency_calc(cost_data, n_samples)
    keys = base_keys.copy()
    frequencies = base_frequencies.copy()
    math_ozh: int = get_cleared_mean(frequencies)
    interesting_part_ind = len(keys) // 3
    if len(frequencies) < 2:
        return keys, frequencies
    while frequencies[interesting_part_ind] > math_ozh // 2 and interesting_part_ind < len(frequencies):  # todo
        interesting_part_ind += 1
    while True:
        if 0 < interesting_part_ind < len(frequencies):
            right_key = keys[interesting_part_ind]
            right_frequency: int = 0
            for i in range(interesting_part_ind, len(frequencies)):
                right_frequency += frequencies[i]
            left_costs: list[float] = []
            for cost in cost_data:
                if cost < keys[interesting_part_ind - 1]:
                    left_costs.append(cost)
                else:
                    break
            keys, frequencies = frequency_calc(left_costs, n_samples - 1)
            keys.append(right_key)
            frequencies.append(right_frequency)
            if right_frequency > get_cleared_mean(frequencies):
                interesting_part_ind += 1
                frequencies = base_frequencies
                keys = base_keys
            else:
                break
        else:
            break
    return list(map(int, keys)), list(map(int, frequencies))


def get_frequency_stats_with_jorm(niche: Niche) -> tuple[list[float], list[int]]:
    cost_data: ndarray[float] = niche.cost_data.copy()
    n_samples: int = int(len(cost_data) * 0.1)
    if len(cost_data) <= 0:
        return [], []
    base_keys, base_frequencies = frequency_calc_new(cost_data, n_samples)
    keys = base_keys.copy()
    frequencies = base_frequencies.copy()
    math_ozh: int = get_cleared_mean(frequencies)
    interesting_part_ind = len(keys) // 3
    if len(frequencies) < 2:
        return keys, frequencies
    while frequencies[interesting_part_ind] > math_ozh // 2 and interesting_part_ind < len(frequencies):  # todo
        interesting_part_ind += 1
    while True:
        if 0 < interesting_part_ind < len(frequencies):
            right_key = keys[interesting_part_ind]
            right_frequency: int = 0
            for i in range(interesting_part_ind, len(frequencies)):
                right_frequency += frequencies[i]
            left_costs: list[float] = []
            for cost in cost_data:
                if cost < keys[interesting_part_ind - 1]:
                    left_costs.append(cost)
                else:
                    break
            keys, frequencies = frequency_calc(left_costs, n_samples - 1)
            keys.append(right_key)
            frequencies.append(right_frequency)
            if right_frequency > get_cleared_mean(frequencies):
                interesting_part_ind += 1
                frequencies = base_frequencies
                keys = base_keys
            else:
                break
        else:
            break
    return list(map(int, keys)), list(map(int, frequencies))
