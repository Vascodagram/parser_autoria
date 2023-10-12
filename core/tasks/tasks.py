import asyncio

from main import main
from .config_celery import app


@app.task
def parsing_website():
    asyncio.run(main())


parsing_website.apply_async()
