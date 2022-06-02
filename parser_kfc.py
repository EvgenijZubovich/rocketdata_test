from dataclasses import dataclass, asdict
import requests
import json


@dataclass
class Data:
    address: str
    latlon: list
    name: str
    phones: list
    working_hours: list


URL = 'https://api.kfc.com/api/store/v2/store.get_restaurants?showClosed=true'

response = requests.get(URL)
kfc_data = response.json()
data_set = kfc_data.get('searchResults')

days_map = {
    1: 'пн',
    2: 'вт',
    3: 'ср',
    4: 'чт',
    5: 'пт',
    6: 'сб',
    7: 'вс'
}

restaurants_objects = []

for restaurant_data in data_set:
    address = restaurant_data.get('storePublic').get('contacts').get('streetAddress').get('ru')
    if not address:
        continue
    address_list = address.split(', ')[1:]
    result_address = ', '.join(address_list)
    if not result_address:
        continue
    working_hours = []
    if working_hours_data := restaurant_data.get('storePublic').get('openingHours').get('regularDaily'):
        for working_hour in working_hours_data:
            working_hours.append(
                f'{days_map.get(working_hour.get("weekDay"))} {working_hour.get("timeFrom")}-{working_hour.get("timeTill")}')
    else:
        working_hours.append('closed')
    data_obj = Data(
        address=result_address,
        latlon=restaurant_data.get('storePublic').get('contacts').get('coordinates').get('geometry').get('coordinates'),
        name=restaurant_data.get('storePublic').get('title').get('ru'),
        phones=[
            restaurant_data.get(
                'storePublic',
            ).get(
                'contacts',
            ).get(
                'phoneNumber',
            ).replace(
                ',',
                '',
            ).replace(
                'доб. ', '').split(
                ' ',
            ),
        ],
        working_hours=working_hours
    )
    restaurants_objects.append(asdict(data_obj))

with open('./kfc_result.json', 'w') as file:
    json.dump(restaurants_objects, file, indent=2, ensure_ascii=False)
