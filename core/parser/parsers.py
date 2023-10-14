import json
import logging
import re

from . import format

from bs4 import BeautifulSoup


def get_cnt_pages(obj_soup: BeautifulSoup):
    cnt_str = obj_soup.body.find(
        'span', id='regionTooltipSearchResultsCount').text

    cnt = int(cnt_str.replace(' ', ''))
    return cnt


def get_links_of_page(obj_soup: BeautifulSoup):
    result = []

    link_elements = obj_soup.body.find_all('a', class_='address')

    for link_element in link_elements:
        href = link_element.get('href', '')

        if not href:
            logging.warning('Link not found')

        result.append(href)

    return result


def get_phones(obj_soup: BeautifulSoup):
    ...


def get_data(url, obj_soup: BeautifulSoup):

    price_element = obj_soup.body.find('div', class_='price_value').text
    price = re.sub(r'\D', '', price_element)

    raw_odometer = obj_soup.body.find(
        'div', class_='base-information bold').text

    username = obj_soup.body.find('div', class_='seller_info_name bold')
    if not username:
        username = 'No name'
    else:
        username = username.text.replace(' ', '')

    description = obj_soup.body.find('div', class_='full-description')
    if not description:
        description = ''
    else:
        description = description.text

    t_check = obj_soup.body.find('div', class_='t-check')
    car_number = t_check.find('span', class_='state-num ua')
    if not car_number:
        car_number = ''
    else:
        car_number.find('span').extract()
        car_number = car_number.text

    car_vin = t_check.find('span', class_='label-vin')
    car_vin_only = obj_soup.body.find('span', class_='vin-code')
    if car_vin:
        car_vin = car_vin.text

    elif car_vin_only:
        car_vin = car_vin_only.text

    images = obj_soup.body.find('div', id='photosBlock')
    image = images.find('script', type='application/ld+json')
    if not image:
        image = ''
    else:
        images_data = json.loads(image.text)
        image = images_data['image'][1]['image']

    cnt_images = images.find('div', class_='count-photo left')
    if not cnt_images:
        cnt_images = 0
    else:
        cnt_images = cnt_images.find('span', class_='dhide').text
        cnt_images = int(cnt_images.replace('з ', ''))

    return {
        'url': url,
        'title': description,
        'price_usd': int(price),
        'odometer': format.format_odometer(raw_odometer),
        'username': username,
        'phone_number': '',
        'image_url': image,
        'images_count': cnt_images,
        'car_number': car_number,
        'car_vin': car_vin
    }
