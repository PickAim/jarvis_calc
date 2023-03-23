import json

from jorm.market.infrastructure import HandlerType

from jarvis_calc.files.file_constants import commission_json, commission_csv

COMMISSION_KEY = "commission"
RETURN_PERCENT_KEY = "return_percent"


def resolve_commission_file(filepath: str) -> None:
    with open(filepath, "r") as file:
        commission_dict: dict = {}
        lines: list[str] = file.readlines()
        for line in lines:
            splitted: list[str] = line.split(";")
            if splitted[0] not in commission_dict.keys():
                commission_dict[splitted[0]] = {}
            commission_dict[splitted[0]][splitted[1]] = {
                COMMISSION_KEY: {
                    str(HandlerType.MARKETPLACE): float(splitted[2]) / 100,
                    str(HandlerType.PARTIAL_CLIENT): float(splitted[3]) / 100,
                    str(HandlerType.CLIENT): float(splitted[4]) / 100
                },
                RETURN_PERCENT_KEY: int(splitted[5].replace("%", ""))
            }
        json_string: str = json.dumps(commission_dict, indent=4, ensure_ascii=False)
        with open(commission_json, "w") as out_file:
            out_file.write(json_string)


def get_commission_for(category: str, niche: str, own_type: str) -> float:
    with open(commission_json, "r") as json_file:
        commission_data: dict = json.load(json_file)
        return commission_data[category][niche][COMMISSION_KEY][own_type]


def get_return_percent_for(category: str, niche: str) -> float:
    with open(commission_json, "r") as json_file:
        commission_data: dict = json.load(json_file)
        return commission_data[category][niche][RETURN_PERCENT_KEY] / 100


def main():
    resolve_commission_file(commission_csv)


if __name__ == '__main__':
    main()
