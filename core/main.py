import asyncio
import json
import logging
import math

from collections import defaultdict

from utils.db import (async_db_session, table_exists, create_car_table,
                      insert_car_data)
from utils.other import iter_chunks, fetch_soup
from utils.http_cli import async_request
from parser import format, parsers

logging.basicConfig(level=logging.INFO)

counter = defaultdict(list)


URL = 'https://auto.ria.com/uk/search/'

PARAMS = {
    'indexName': 'auto,order_auto',
    'categories.main.id': 1,
    'price.USD.lte': 3000,
    'country.import.usa.not': -1,
    'abroad.not': 0,
    'price.currency': 1,
    'page': 0,
    'size': 100
}


async def init_db():
    session = await async_db_session()

    create = await table_exists(session)

    if not create:
        await create_car_table(session)
        logging.info(' Table Car created!!!')

    else:
        logging.info('The Car table has already been created!!!')

    await session.close()


async def fetch_pages(chunk_size):
    """
    the function returns a list with all links by the specified filter
    """
    result = []

    resp = await async_request(url=URL, params=PARAMS)

    if resp.status != 200:
        logging.warning(f'Page count parser, status code: {resp.status}')
        return

    cnt_pages = parsers.get_cnt_pages(fetch_soup(resp.content))

    logging.info(f'Car count {cnt_pages}')

    cnt_pages = math.ceil(cnt_pages / PARAMS['size'])

    logging.info(f'Pages count {cnt_pages}')

    tasks = []

    for page in range(0, cnt_pages):
        params = PARAMS.copy()
        params['page'] = page

        tasks.append(
            async_request(url=URL, params=params)
        )

    for chunk in iter_chunks(tasks, size=chunk_size):
        res = await asyncio.gather(*chunk)

        for response in res:
            counter["cnt_pages"].append(response.status)

            result.extend(
                parsers.get_links_of_page(fetch_soup(response.content))
            )

        logging.info(f'Collected {len((counter["cnt_pages"]))} pages')

    return result


async def main(value, chunk_size):
    session = await async_db_session()

    tasks = []
    for link in value:
        tasks.append(fetch_url(link))

    for chunk in iter_chunks(tasks, size=chunk_size):
        res = await asyncio.gather(*chunk)
        await insert_car_data(session, res)

    await session.close()


async def fetch_url(url):
    resp = await async_request(url)

    if resp.status != 200:
        logging.warning(f'Bad request, status code: {resp.status}')
        return

    result = parsers.get_data(url, fetch_soup(resp.content))
    params_for_phones = parsers.get_params_for_phones(fetch_soup(resp.content))

    user_id = url.split('_')[-1].replace('.html', '')

    resp_phones = await async_request(
        url=f'https://auto.ria.com/users/phones/{user_id}',
        params={
            'hash': params_for_phones['hash'],
            'expires': params_for_phones['expires']
        }
    )

    if resp_phones.status != 200:
        logging.warning(
            f'Bad request for phones link, status code: {resp.status}')
        return

    result['phone_number'] = format.format_phones(
        json.loads(resp_phones.content))

    return result
