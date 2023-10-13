import asyncio
import logging

from main import main, fetch_pages
from .config_celery import app


logging.basicConfig(level=logging.INFO)


@app.task
def parsing_website(data, chunk_size):
    asyncio.run(main(data, chunk_size))


if __name__ == '__main__':
    links_pages = asyncio.run(fetch_pages(chunk_size=20))

    logging.info(f'Received {len(links_pages)} links')

    for links in links_pages:
        parsing_website.apply_async(data=links, chunk_size=20)
