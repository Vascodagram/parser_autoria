import json
import logging
import re

from . import format

from bs4 import BeautifulSoup


def get_cnt_pages(obj_soup: BeautifulSoup):
    html = obj_soup.body.prettify()

    match = re.search(
        r'window\.ria\.server\.resultsCount = Number\((\d+)\);',
        html)

    return int(match.group(1))


def get_links_of_page(obj_soup: BeautifulSoup):
    result = []

    link_elements = obj_soup.body.find_all('a', class_='address')

    for link_element in link_elements:
        href = link_element.get('href', '')

        if not href:
            logging.warning('Link not found')

        result.append(href)

    return result


def has_partial_class(class_name):
    return class_name and 'js-user-secure-' in class_name


def get_params_for_phones(obj_soup: BeautifulSoup):
    # ticket_status = obj_soup.find('div', class_='ticket-status-0')
    script_data, = obj_soup.find_all(
        'script', lambda cls: cls and 'js-user-secure-' in cls)

    return {
        'hash': script_data['data-hash'],
        'expires': script_data['data-expires']
    }


def get_data(url, obj_soup: BeautifulSoup):
    price_element = obj_soup.body.find('div', class_='price_value')
    price = ''
    if price_element:
        price = re.sub(r'\D', '', price_element.text)

    raw_odometer = obj_soup.body.find(
        'div', class_='base-information bold').text

    username = obj_soup.body.find('div', class_='seller_info_name bold')
    if not username:
        username = 'No name'
    else:
        username = username.text.strip()

    description = obj_soup.body.find('div', class_='full-description')
    if not description:
        description = ''
    else:
        description = description.text

    t_check = obj_soup.body.find('div', class_='t-check')
    car_number = ''
    if t_check:

        car_number = t_check.find('span', class_='state-num ua')
        if not car_number:
            car_number = ''
        else:
            car_number.find('span').extract()
            car_number = car_number.text.rstrip()

    car_vin = ''
    if t_check:
        car_vin = t_check.find('span', class_='label-vin')
        car_vin_only = obj_soup.body.find('span', class_='vin-code')
        if car_vin:
            car_vin = car_vin.text

        elif car_vin_only:
            car_vin = car_vin_only.text

    images = obj_soup.body.find('div', id='photosBlock')
    image = ''

    if images and images.find('script', type='application/ld+json'):
        raw_images = images.find('script', type='application/ld+json')
        try:
            images_data = json.loads(raw_images.text)
            image = images_data.get('image')
            image = image[1]['image'] if image else ''
        except (json.decoder.JSONDecodeError, IndexError):
            image = ''

    cnt_img = 0
    if images:
        div_images = images.find('div', class_='count-photo left')

        if div_images:
            cnt_images = div_images.find('span', class_='dhide').text
            cnt_img = int(cnt_images.replace('з ', ''))

    return {
        'url': url,
        'title': description,
        'price_usd': int(price),
        'odometer': format.format_odometer(raw_odometer),
        'username': username,
        'phone_number': '',
        'image_url': image,
        'images_count': cnt_img,
        'car_number': car_number,
        'car_vin': car_vin,
    }
