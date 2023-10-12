from bs4 import BeautifulSoup


def get_cnt_pages(obj_soup: BeautifulSoup):
    cnt = 0

    spans = obj_soup.find_all('div', class_='unstyle pager')
    print(spans)
    return cnt


def get_links(bj_soup: BeautifulSoup):
    result = []

    return result


def get_phones(bj_soup: BeautifulSoup):
    ...


def get_data(bj_soup: BeautifulSoup):
    return {}