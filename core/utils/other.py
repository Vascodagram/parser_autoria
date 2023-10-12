import bs4


def fetch_soup(content, *args, **kwargs):
    return bs4.BeautifulSoup(content, 'html.parser', *args, **kwargs)


def iter_chunks(data, size=1000):
    for i in range(0, len(data), size):
        yield data[i:i + size]
