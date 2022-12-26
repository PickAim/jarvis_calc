import numpy as np

from utils.request_utils import get_object_name


def frequency_calc(costs: list[float], n_samples: int) -> tuple[list[float], list[int]]:
    res = np.histogram(costs, n_samples)
    return list(res[1][1:]), list(res[0])


def get_cleared_mean(lst: list[int]) -> int:
    result: int = 0
    clear_frequency = np.array([x for x in lst if x != 0])
    for freq in clear_frequency:
        result += freq
    return int(result / len(clear_frequency))


def get_frequency_stats(cost_data: list[float], n_samples: int) -> tuple[list[float], list[int]]:
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
    return keys, frequencies


def sort_by_len_alphabet(names: list[str]) -> list[str]:
    length_dict: [int, list[str]] = {}
    for name in names:
        if not length_dict.__contains__(len(name)):
            length_dict[len(name)] = [name]
            continue
        length_dict[len(name)].append(name)
    sorted_tuples: list = sorted(length_dict.items())
    result: list[str] = []
    for length_tuple in sorted_tuples:
        result.extend(sorted(length_tuple[1]))
    return result


def get_nearest_keywords(word: str) -> list[str]:
    names: list[str] = get_object_name(word)
    scored_dict: dict[float, list[str]] = score_object_names(word, names)
    result: list[str] = []
    for score in scored_dict.keys():
        result.extend(sort_by_len_alphabet(scored_dict[score]))
    return result


def score_object_names(searched_object: str, object_names: list[str]) -> dict[float, list[str]]:
    searched_object = searched_object.lower()
    good_match: float = 5.0
    intermediate_match: float = 2.5
    poor_match: float = 1.0
    searched_words = []
    if len(searched_object) > 1:
        searched_words: list[str] = searched_object.split(" ")
        if len(searched_words) == 1:
            mid_idx: int = len(searched_object) // 2
            searched_words = [searched_object[:mid_idx], searched_object[mid_idx:]]
    lower_names: list[str] = [lower_name.lower() for lower_name in object_names]
    result: dict[float, list[str]] = {good_match: [], intermediate_match: [], poor_match: []}
    for name in lower_names:
        words: list[str] = [word + " " for word in name.split(" ")]
        if words[: len(words) // 2].__contains__(searched_object + " ") \
                or words.__contains__(searched_object + " ") and len(words) < 3:
            result[good_match].append(name)
            continue
        flag: bool = False
        for word_to_match in searched_words:
            if any_contains(word_to_match, words):
                result[intermediate_match].append(name)
                flag = True
                break
        if flag:
            continue
        result[poor_match].append(name)
    return result


def any_contains(text_to_search: str, words: list[str]) -> bool:
    sentence: str = "".join(words)
    for word in words:
        if word.__contains__(text_to_search) and sentence.index(text_to_search) < len(sentence) // 2:
            return True
    return False
