import json
from files.file_constants import commission_json, commission_csv

WB_OWNED: str = "wb"
SELLER_OWNED: str = "owned"
ALL_TO_SELLER: str = "self"


def resolve_commission_file(filepath: str) -> None:
    with open(filepath, "r") as file:
        commission_dict: dict[str, dict[str, dict[str, float]]] = {}
        lines: list[str] = file.readlines()
        for line in lines:
            splitted: list[str] = line.split(";")
            if not commission_dict.keys().__contains__(splitted[0]):
                commission_dict[splitted[0]] = {}
            commission_dict[splitted[0]][splitted[1]] = {
                WB_OWNED: float(splitted[2]) / 100,
                SELLER_OWNED: float(splitted[3]) / 100,
                ALL_TO_SELLER: float(splitted[4]) / 100
            }
        json_string: str = json.dumps(commission_dict, indent=4, ensure_ascii=False)
        with open(commission_json, "w") as out_file:
            out_file.write(json_string)


def get_commission_for(category: str, niche: str, own_type: str) -> float:
    with open(commission_json, "r") as json_file:
        commission_data: dict[str, dict[str, dict[str, float]]] = json.load(json_file)
        return commission_data[category][niche][own_type]


def main():
    resolve_commission_file(commission_csv)


if __name__ == '__main__':
    main()
