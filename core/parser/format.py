import re
from dataclasses import dataclass


@dataclass
class CarData:
    id: str
    url: str
    title: str
    price_usd: float
    odometer: int
    username: str
    phone_number: str
    image_url: str
    images_count: int
    car_number: str
    car_vin: str
    datetime_found: str

    def as_dict(self):
        return self.__dict__


def format_data(raw_data):
    return


def format_odometer(value):
    if 'тис. км пробіг' in value:
        value = int(value.replace('тис. км пробіг', '').replace(' ', '')) * 1000

    return value


def format_phones(value):
    raw_phone = value['formattedPhoneNumber']
    phone = re.sub(r'[() ]', '', raw_phone)

    return '+38' + phone
