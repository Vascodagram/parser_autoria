import json
import os

import aiohttp
import aiopg

from dataclasses import dataclass

dsn = 'dbname={dbname} user={user} password={password} host={host}'


async def go():
    return await aiopg.connect(
        database=os.getenv('POSTGRES_DB', 'autoria'),
        user=os.getenv('POSTGRES_USER', 'AutoRia'),
        password=os.getenv('POSTGRES_PASSWORD', 'AutoRia'),
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', 5431)
    )


def iter_chunks(data, size=1000):
    for i in range(0, len(data), size):
        yield data[i:i + size]


@dataclass
class Response:
    status: int
    content: str
    data: dict = dict


async def async_request(
        url,
        method='GET',
        params=None,
        headers=None,
        data=None,
        request_timeout=None,
        verify_ssl=True
):
    result = None
    async with aiohttp.ClientSession() as session:
        async with session.request(
                method=method,
                url=url,
                data=json.dumps(data) if data else None,
                params=params,
                headers=headers,
                timeout=request_timeout,
                ssl=verify_ssl
        ) as response:
            status = response.status
            content = await response.read()

    return Response(
        status=status,
        content=content.decode()
    )
