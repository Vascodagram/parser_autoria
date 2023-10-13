import asyncio
import logging
import math

from utils.db import (async_db_session, table_exists, create_car_table,
                      insert_car_data)
from utils.other import iter_chunks, fetch_soup
from utils.http_cli import async_request
from parser import format, parsers

from collections import defaultdict

logging.basicConfig(level=logging.INFO)

counter = defaultdict(list)

URL = 'https://auto.ria.com/uk/search/'
PARAMS = {
    'indexName': 'auto,order_auto',
    'categories.main.id': 1,
    'country.import.usa.not': -1,
    'abroad.not': 0,
    'price.currency': 1,
    'page': 0,
    'size': 100
}


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
    cnt_pages = math.ceil(cnt_pages / PARAMS['size'])

    tasks = []
    for page in range(0, cnt_pages):
        PARAMS['page'] = page

        tasks.append(asyncio.create_task(
            async_request(
                url=URL,
                params=PARAMS
            )
        ))

    for chunk in iter_chunks(tasks, size=chunk_size):
        res = await asyncio.gather(*chunk)

        for response in res:
            counter["cnt_pages"].append(response.status)

            result.extend(
                parsers.get_links_of_page(fetch_soup(response.content))
            )
        break

        logging.info(f'Collected {len((counter["cnt_pages"]))} pages')

    return result


async def main(value, chunk_size):
    session = await async_db_session()

    create = table_exists(session)

    if not create:
        await create_car_table(session)
        logging.info(' Table Car created!!!')

    else:
        logging.info('The Car table has already been created!!!')

    tasks = []
    for link in value:
        tasks.append(asyncio.create_task(fetch_url(link)))

    for chunk in iter_chunks(tasks, size=chunk_size):
        res = await asyncio.gather(*chunk)

        break
        await insert_car_data(session, res)

    await session.close()


async def fetch_url(url):
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

    if resp_phones.status != 200:
        logging.warning(
            f'Bad request for phones link, status code: {resp.status}')
        return

    raw_data['phone_number'] = parsers.get_phones(resp_phones)

    data = format.format_data(raw_data)

    return data

if __name__ == '__main__':
    links = asyncio.run(fetch_pages(1))
    asyncio.run(main(links, chunk_size=1))
