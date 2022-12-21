import os
from os.path import join, abspath

splitted: list[str] = abspath(__file__).split(os.sep)[:-1]
splitted[0] += os.sep
rootpath = join(*splitted)

data_path = join(rootpath, "data")
out_path = join(rootpath, "out")

