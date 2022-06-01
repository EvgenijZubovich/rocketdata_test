import requests
from dataclasses import dataclass, asdict
import json
from lxml import html
import re
from pprint import pprint

URL = 'https://monomax.by/map'
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0', 'accept': '*/*'}


@dataclass
class Data:
    address: str
    latlon: list
    name: str
    phones: list


response = requests.get(URL, headers=HEADERS)
page = html.fromstring(response.content)
page_js = page.xpath('//script[contains(text(), "ymaps.ready(init);")]/text()')[0].replace('\n', '')
shops = re.findall(r'ymaps.Placemark.+?}\s+\)', page_js)
shop_objects = []
for shop in shops:
    lat_lon = re.findall(r'\[.+?]', shop)
    text_list = re.findall(r"\'.+?'", shop)
    address = text_list[0][1:-1]
    if 'Минск' not in address:
        address = f'Минск, {address}'
    data_obj = Data(
        address=address,
        latlon=[float(i) for i in lat_lon[0][1:-1].split(', ')],
        name='Мономах',
        phones=[text_list[1][1:-1].replace(' ', '').replace('(', '').replace(')', '').split(':')[1]],
    )
    shop_objects.append(asdict(data_obj))

with open('./monomax_result.json', 'w') as file:
    json.dump(shop_objects, file, indent=2, ensure_ascii=False)
