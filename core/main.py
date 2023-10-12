import asyncio
import json
import logging
import os

from collections import defaultdict

from utils import async_request, iter_chunks, go

logging.basicConfig(level=logging.INFO)

counter = defaultdict(list)


async def await_db_session(url='http://db:5432/'):
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    db = os.getenv('POSTGRES_DB')

    session = None  # SQLAlchemy session

    return session


async def afetch_urls(urls):
    session = await await_db_session()
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
    url_phones = 'https://auto.ria.com/users/phones/'

    resp = await async_request(url)

    if resp.status != 200:
        logging.warning(f'Bad request, status code: {resp.status}')
        return

    content = resp.content

    valid_data = data_validation(content)

    id_users, hash, expires = [
        valid_data[v] for v in ['id_users', 'hash', 'expires']
    ]

    resp_phones = await async_request(
        url=f'https://auto.ria.com/users/phones/{id_users}',
        params={
            'hash': hash,
            'expires': expires
        }
    )

    if resp_phones.status != 200:
        logging.warning(
            f'Bad request for phones link, status code: {resp.status}')
        return

    raw_phones = json.dumps(resp_phones.content)

    return {
        'url': valid_data.get('url', ''),
        'title': valid_data.get('title', ''),
        'price_usd': valid_data.get('price_usd', ''),
        'odometer': format_odometer(valid_data.get('odometer')),
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
    conn = asyncio.run(go())