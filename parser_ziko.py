import requests
from dataclasses import dataclass, asdict
import json
from lxml import html

URL = 'https://www.ziko.pl/wp-admin/admin-ajax.php?action=get_pharmacies'
PAGE_URL = 'https://www.ziko.pl/lokalizator'
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0', 'accept': '*/*'}


@dataclass
class Data:
    address: str
    latlon: list
    name: str
    phones: list
    working_hours: list


page_response = requests.get(PAGE_URL, headers=HEADERS)
page = html.fromstring(page_response.content)

response = requests.get(URL, headers=HEADERS)
ziko_data = response.json()
apteks_objects = []

cards = page.xpath('/html/body/div[3]/table/tbody/tr')

for card in cards:
    card_id = card.xpath('@data-mp-id')[0]
    name = card.xpath('./td[@class="mp-table-dermo"]/span[@class="mp-pharmacy-head"]/text()')[0].rstrip().lstrip()
    card_info = card.xpath("./td[@class='mp-table-address']//text()")
    phones = []
    for info_item in card_info:
        if 'tel.' in info_item:
            phones.append(info_item.replace(' ', '').replace('tel.', ''))

        if 'Infolinia:' in info_item:
            phones.append(info_item.replace(' ', '').replace('Infolinia:', ''))
    data_aptek = ziko_data.get(card_id)
    working_hours_list = data_aptek.get('mp_pharmacy_hours').replace('niedziela handlowa<br>', 'nie').rstrip(
        '<br>').split('<br>')
    if "niedziela niehandlowa" in working_hours_list:
        working_hours_list = working_hours_list[:working_hours_list.index("niedziela niehandlowa")]
    data_obj = Data(
        address=f'{data_aptek.get("city_name")[0]}, {data_aptek.get("address")}',
        latlon=[float(data_aptek.get('lat')), float(data_aptek.get('lng'))],
        name=name,
        phones=phones,
        working_hours=working_hours_list
    )

    apteks_objects.append(asdict(data_obj))

with open('./ziko_result.json', 'w') as file:
    json.dump(apteks_objects, file, indent=2, ensure_ascii=False)
