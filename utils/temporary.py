import json
from files.file_constants import commission_json, commission_csv


def resolve_commission_file(filepath: str) -> None:
    with open(filepath, "r") as file:
        commission_dict: dict[str, dict[str, dict[str, float]]] = {}
        lines: list[str] = file.readlines()
        for line in lines:
            splitted: list[str] = line.split(";")
            if not commission_dict.keys().__contains__(splitted[0]):
                commission_dict[splitted[0]] = {}
            commission_dict[splitted[0]][splitted[1]] = {
                "wb": float(splitted[2]) / 100,
                "owned": float(splitted[3]) / 100,
                "self": float(splitted[4]) / 100
            }
        json_string: str = json.dumps(commission_dict, indent=4, ensure_ascii=False)
        with open(commission_json, "w") as out_file:
            out_file.write(json_string)


def main():
    resolve_commission_file(commission_csv)


if __name__ == '__main__':
    main()
