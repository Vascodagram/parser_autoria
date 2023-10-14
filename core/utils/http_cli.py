import json

import brotli
import aiohttp

from dataclasses import dataclass


aiohttp.ClientResponse._decode_compression = brotli.decompress

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
              'image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,uk;q=0.8,ru;q=0.7',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ('
                  'KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
}


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
        verify_ssl=False
):

    async with aiohttp.ClientSession() as session:
        async with session.request(
                method=method,
                url=url,
                data=json.dumps(data) if data else None,
                params=params,
                headers=HEADERS if not headers else headers,
                timeout=request_timeout,
                ssl=verify_ssl
        ) as response:
            status = response.status
            content = await response.read()

    return Response(
        status=status,
        content=content.decode()
    )
