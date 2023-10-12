import asyncio
import logging
import os

import bs4

from celery import Celery

from main import afetch_urls
from utils import async_request


REDIS_DNS = os.getenv('REDIS_DNS', 'redis://localhost:6378/0')

app = Celery('parser_avtoria', backend=REDIS_DNS)

logging.basicConfig(level=logging.INFO)


@app.task
def parsing_avtoria():
    asyncio.run(parsing_data())


async def parsing_data():
    url = 'https://auto.ria.com/uk/search/'
    params = {
        'indexName': 'auto,order_auto',
        'categories.main.id': 1,
        'country.import.usa.not': -1,
        'price.currency': 1,
        'page': 0,
        'size': 100
    }

    cnt_page = await get_cnt_pages(url, params)

    for page in range(0, cnt_page):

        params['page'] = page

        resp = await async_request(
            url=url,
            params=params
        )

        links = parsing_links()

        await afetch_urls(links)

        logging.info(f'Page {page} of {cnt_page}')


async def get_cnt_pages(url, params):
    resp = await async_request(
        url=url,
        params=params
    )

    soup = bs4.BeautifulSoup(resp.content, 'html.parser')

    print(soup)


def parsing_links(content):
    ...
