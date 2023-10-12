import asyncio
import json
import logging

from utils.db import async_db_session, table_exists, create_car_table
from utils.other import iter_chunks, fetch_soup
from utils.http_cli import async_request
from parser import format, parsers

from collections import defaultdict

logging.basicConfig(level=logging.INFO)
counter = defaultdict(list)


async def main():
    url = 'https://auto.ria.com/uk/search/'
    params = {
        'indexName': 'auto,order_auto',
        'categories.main.id': 1,
        'country.import.usa.not': -1,
        'price.currency': 1,
        'page': 0,
        'size': 100
    }
    session = await async_db_session()

    create = table_exists(session)

    if not create:
        await create_car_table(session)
        logging.info(' Table Car created')

    else:
        logging.info('The Car table has already been created')

    resp = await async_request(url=url, params=params)

    if resp.status != 200:
        logging.warning(f'Page count parser, status code: {resp.status}')
        return

    cnt_page = parsers.get_cnt_pages(fetch_soup(resp.content))

    for page in range(0, cnt_page):
        params['page'] = page

        resp = await async_request(
            url=url,
            params=params
        )

        links = parsers.get_links(fetch_soup(resp.content))

        await async_parsing_urls(links)

        logging.info(f'Page {page} of {cnt_page}')

    session.close()


async def async_parsing_urls(session, urls):
    tasks = []

    for url in urls:
        tasks.append(asyncio.create_task(fetch_url(url)))

    for chunk in iter_chunks(tasks, 20):
        result = await asyncio.gather(*chunk)

        for data in result:

            if not data:
                continue

            await insert_db(session, data)

        counter['parse_urls'].extend(chunk)

        logging.info(
            f' Data inserted into the database {len(counter["parse_urls"])}'
        )


async def fetch_url(url):
    # url_phones = 'https://auto.ria.com/users/phones/'

    resp = await async_request(url)

    if resp.status != 200:
        logging.warning(f'Bad request, status code: {resp.status}')
        return

    raw_data = parsers.get_data(fetch_soup(resp.content))

    resp_phones = await async_request(
        url=f'https://auto.ria.com/users/phones/{raw_data["id_user"]}',
        params={
            'hash': raw_data['hash'],
            'expires': raw_data['expires']
        }
    )

    raw_data['phones'] = resp_phones

    data = parsers.format_data(raw_data)

    if resp_phones.status != 200:
        logging.warning(
            f'Bad request for phones link, status code: {resp.status}')
        return

    raw_phones = json.dumps(resp_phones.content)

    return {
        'url': data.get('url', ''),
        'title': data.get('title', ''),
        'price_usd': data.get('price_usd', ''),
        'odometer': format_odometer(data.get('odometer')),
        'phone': format_phones(raw_phones)
        # ...
    }


def format_phones(string):
    """
    format the phone number to be entered into the database
    """
    ...


def format_odometer(string):
    """
    format the odometer to be entered into the database
    """
    ...


async def insert_db(session, data):
    '''
    here you need to do an asynchronous insertion of data into a database table
    '''
    ...


def data_validation(content, table='car'):
    '''
    Here you need to write code that will validate the data,
    convert it to the appropriate format for a particular table,
    and return the finished structure in the form of a dictionary
    where the keys are the names of the fields in the table
    '''
    ...


if __name__ == '__main__':
    conn = asyncio.run(async_db_session())