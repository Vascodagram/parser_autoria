from bs4 import BeautifulSoup


def get_cnt_pages(obj_soup: BeautifulSoup):
    cnt = 0

    spans = obj_soup.find('div', id='searchPagination').find('span', class_='page-item dhide text-c')
    print(spans)
    return cnt


def get_links_of_page(bj_soup: BeautifulSoup):
    result = []

    return result


def get_phones(bj_soup: BeautifulSoup):
    ...


def get_data(bj_soup: BeautifulSoup):
    return {}
