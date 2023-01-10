import os

splitted: list[str] = os.path.abspath(__file__).split(os.sep)[:-1]
splitted[0] += os.sep
file_dir: str = os.path.join(*splitted)

commission_json = os.path.join(file_dir, "commission.json")
commission_csv = os.path.join(file_dir, "commission.csv")
