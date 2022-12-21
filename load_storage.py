import requests


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


def get_storage_data(product_ids: [int]) -> dict[int, dict[int, int]]:
    main_dict: dict[int, dict[int, int]] = {}
    for product_id in product_ids:
        dicts = get_storage_dict(product_id)
        main_dict[product_id] = dicts
    return main_dict
