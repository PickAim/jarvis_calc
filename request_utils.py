import requests
import aiohttp
import asyncio

from requests.adapters import HTTPAdapter
from asyncio import Task
from aiohttp import ClientSession
from requests import Response, Session
from datetime import datetime, timedelta
from os.path import join


def get_parent():
    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
    session.mount('http://', adapter)
    response = session.get('https://suppliers-api.wildberries.ru/content/v1/object/parent/all',
                           headers={
                               'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                                                '.eyJhY2Nlc3NJRCI6IjZkNDVmMmRjLTQ5ODEtNDFlOS1hMzRkLTlhNDA5YmY2MGZiMSJ9.'
                                                '1VoUp9Od9dzSWSNVSQjQnRujUvqOUY4oxO-pZXAqI1Q'})

    json_code = response.json()
    parent_category = []
    for data in json_code['data']:
        parent_category.append(data['name'])
    return parent_category


def get_object_name(text : str):
    object_name_list = []
    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
    session.mount('http://', adapter)
    response = session.get('https://suppliers-api.wildberries.ru/content/v1/object/all?name=' + text
                           +'&top=100',
                           headers={
                               'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
                                                '.eyJhY2Nlc3NJRCI6IjZkNDVmMmRjLTQ5ODEtNDFlOS1hMzRkLTlhNDA5YmY2MGZiMSJ9.'
                                                '1VoUp9Od9dzSWSNVSQjQnRujUvqOUY4oxO-pZXAqI1Q'})
    json_code = response.json()
    for data in json_code['data']:
        object_name_list.append(data['objectName'])
    return object_name_list


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


def get_storage_dict(product_id: int) -> dict[int, int]:
    mass = []
    session = requests.Session()
    url = f'https://card.wb.ru/cards/detail?spp=27&regions=64,58,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48' \
          f'&pricemarginCoeff=1.0&reg=1&appType=1&emp=0&locale=ru&lang=ru&curr=rub' \
          f'&dest=-1221148,-140294,-1701956,123585768&nm={product_id}'
    request = session.get(url)
    json_code = request.json()
    session.close()
    for product in json_code['data']['products']:
        for data in product['sizes']:
            mass.append(data['stocks'])  # TODO it's not my todo @Pelidyai
    warehouse_leftover_dict = {}
    for product in mass:
        for data_storage in product:
            warehouse_leftover_dict[data_storage['wh']] = data_storage['qty']
            # TODO think about same name for warehouse, but different leftovers -> it will squash to the last one value
    return warehouse_leftover_dict
