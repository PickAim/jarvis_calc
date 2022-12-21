from asyncio import AbstractEventLoop, Task

import requests

from os.path import exists
from os import mkdir
from os import listdir
from os.path import isfile, join
from datetime import datetime, timedelta

import aiohttp
import asyncio

from aiohttp import ClientSession
from requests import Response, Session


async def get_page_data(session: ClientSession, product_id: int) -> list[float]:
    avr_mass: list[float] = []
    url: str = 'https://wbx-content-v2.wbstatic.net/price-history/'+str(product_id)+'.json?'
    async with session.get(url=url) as request:
        response_status: int = request.status
        if response_status != 200:
            pass
        else:
            json_code = await request.json()
            summary_of_costs: float = 0
            count: int = 1
            last_month = datetime.now() - timedelta(days=30)
            for obj in json_code:
                time_data = datetime.fromtimestamp(obj['dt'])
                if time_data > last_month:
                    summary_of_costs += obj['price']['RUB']
                    count += 1
            if summary_of_costs != 0:
                avr_mass.append(summary_of_costs / count)
            else:
                avr_mass.append(json_code[len(json_code) - 1]['price']['RUB'])
        return avr_mass


async def load_all_product_niche(text: str, output_dir: str, pages_num: int) -> None:
    iterator_page: int = 1
    temp_mass: list[str] = []
    name_and_id_list: list[tuple[str, int]] = []
    session: Session = requests.Session()
    while True:
        uri: str = f'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=2,12,7,3,6,21,16' \
              f'&curr=rub&dest=-1221148,-140294,-1751445,-364763&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0' \
              f'&query={text}&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false&page={str(iterator_page)}'
        request: Response = session.get(
            uri
        )
        json_code = request.json()
        temp_mass.append(str(json_code))
        if 'data' not in json_code:
            break
        for product in json_code['data']['products']:
            name_and_id_list.append((product['name'], product['id']))  # TODO we collect names - for what?
        iterator_page += 1
        if pages_num != -1 and iterator_page > pages_num:
            break
    session.close()
    async with aiohttp.ClientSession() as clientSession:
        tasks: list[Task] = []
        for name_and_id in name_and_id_list:
            task = asyncio.create_task(get_page_data(clientSession, name_and_id[1]))
            tasks.append(task)
        avr_collection: any = await asyncio.gather(*tasks)
        j: int = 0
        with open(join(output_dir, text + ".txt"), 'w', encoding='utf-8') as f:
            for avr_mass in avr_collection:
                for i in range(len(avr_mass)):
                    if j % 10 == 0 and j != 0:
                        f.write("\n")
                    j += 1
                    f.write(str(avr_mass[i]) + ",")
    await clientSession.close()


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
