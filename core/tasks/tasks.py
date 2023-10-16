import asyncio
import logging

from main import main, fetch_pages, init_db
from utils.other import iter_chunks

from tasks.celery_app import app

logging.basicConfig(level=logging.INFO)


@app.task
def parsing_website(links, chunk_size):
    asyncio.run(main(links, chunk_size))


asyncio.run(init_db())
links_pages = asyncio.run(fetch_pages(chunk_size=100))

logging.info(f'Received {len(links_pages)} links')


for lst_links in iter_chunks(links_pages, 100):
    result = parsing_website.delay(lst_links, 100)
