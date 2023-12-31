import os

from celery import Celery

REDIS_DNS = os.getenv('REDIS_DNS', 'redis://localhost:6378/0')

app = Celery(
    'tasks_autoria',
    broker=REDIS_DNS,
)

app.conf.update(
    timezone="UTC"
)
