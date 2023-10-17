import asyncio
import logging

from main import main, fetch_pages, init_db
from utils.other import iter_chunks

from tasks.celery_app import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.task
def parsing_website(links, chunk_size, res):
    asyncio.run(main(links, chunk_size, res))


if not app.control.inspect().registered():
    asyncio.run(init_db())
    links_pages = asyncio.run(fetch_pages(chunk_size=25))

    logging.info(f'Received {len(links_pages)} links')

    _task_name = '|{s_cnt}-{f_cnt}| LINKS COMPLETED'
    _cnt_links = 0
    for lst_links in iter_chunks(links_pages, 10):

        task_name = _task_name.format(
            s_cnt=_cnt_links, f_cnt=_cnt_links + len(lst_links)
        )
        _cnt_links += len(lst_links)

        result = parsing_website.apply_async((lst_links, 10, task_name))
