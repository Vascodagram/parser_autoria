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
    if 'тис.км' in value or 'тыс.км':
        value = int(value) * 1000

    return value
