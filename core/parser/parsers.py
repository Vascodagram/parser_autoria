import logging
import re

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


def get_data(obj_soup: BeautifulSoup):

    price_element = obj_soup.body.find('div', class_='price_value').text
    cleaned_text = re.sub(r'[^\d,]', '', price_element)

    odometer_element = obj_soup.body.find(
        'dl', class_='unstyle').find('span', class_='argument')
    print(odometer_element)
    return {
        'url': '',
        'title': '',
        'price_usd': int(cleaned_text),
        'odometer': '',
        'username': '',
        'phone_number': '',
        'image_url': '',
        'images_count': '',
        'car_number': '',
        'car_vin': ''
    }
