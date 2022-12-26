import asyncio

from asyncio import AbstractEventLoop
from os.path import exists, isfile, join
from os import mkdir, listdir
from request_utils import get_storage_dict, load_all_product_niche


def get_storage_data(product_ids: [int]) -> dict[int, dict[int, int]]:
    main_dict: dict[int, dict[int, int]] = {}
    for product_id in product_ids:
        dicts = get_storage_dict(product_id)
        main_dict[product_id] = dicts
    return main_dict


def load(text: str, output_dir: str, update: bool = False, pages_num: int = -1) -> None:
    only_files: list[str] = []
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    if exists(output_dir):
        only_files = [f.split('.')[0] for f in listdir(output_dir) if isfile(join(output_dir, f))]
    else:
        mkdir(output_dir)
    if not (text in only_files) or update:
        loop: AbstractEventLoop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(load_all_product_niche(text, output_dir, pages_num))
        loop.close()
