import asyncio
import json
import logging

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
            counter["cnt_pages"].extend(response.status)

            result.extend(
                parsers.get_links_of_page(fetch_soup(response.content))
            )

        logging.info(f'Collected {len((counter["cnt_pages"]))} pages')

    return result


async def main(links, chunk_size):
    session = await async_db_session()

    create = table_exists(session)

    if not create:
        await create_car_table(session)
        logging.info(' Table Car created!!!')

    else:
        logging.info('The Car table has already been created!!!')

    tasks = []
    for link in links:
        tasks.append(asyncio.create_task(fetch_url(link)))

    for chunk in iter_chunks(tasks, size=chunk_size):
        result = []

        res = await asyncio.gather(*chunk)

        for response in res:
            result.append(parsers.get_data(response.content))

        await insert_car_data(session, result)

    await session.close()


# async def async_parsing_urls(session, urls):
#     tasks = []
#
#     for url in urls:
#         tasks.append(asyncio.create_task(fetch_url(url)))
#
#     for chunk in iter_chunks(tasks, 20):
#         result = await asyncio.gather(*chunk)
#
#         for data in result:
#
#             if not data:
#                 continue
#
#             await insert_db(session, data)
#
#         counter['parse_urls'].extend(chunk)
#
#         logging.info(
#             f' Data inserted into the database {len(counter["parse_urls"])}'
#         )


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

    raw_data['phones'] = parsers.get_phones(resp_phones)

    data = format.format_data(raw_data)

    return data
