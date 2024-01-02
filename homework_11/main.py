import os
import re
import argparse
import asyncio
import aiofiles
import aiohttp
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://news.ycombinator.com/'
news_dict = {}
link_list = []

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, help='Название папки для сохранения страниц', default='page_download')
    parser.add_argument('-t', type=int, help='Количество секунд между запусками обкачки новостного комбинатора', default=10)
    return parser.parse_args()


def parse_base_page():
    response = requests.get(BASE_URL)
    bs_page = BeautifulSoup(response.text, 'lxml')
    data = bs_page.find_all('span', class_='titleline')
    result = [x.find('a').get('href') for x in data]
    return result


def parse_comments_page():
    response = requests.get(BASE_URL)
    bs_page = BeautifulSoup(response.text, 'lxml')
    data = bs_page.find_all('a', string=re.compile('comments'))
    result = [BASE_URL + x.get('href') for x in data[1:]]
    return result


async def find_href_in_comments(comments_page):
    global link_list
    async with aiohttp.ClientSession() as session:
        response = await session.request('GET', comments_page)
        page = await response.read()
        bs_page = BeautifulSoup(page, 'lxml')
        data = bs_page.find_all('div', class_='comment')
        result = [x.find('a').get('href') for x in data if 'https' in x.find('a').get('href')]
        if result:
            link_list += result
    return result


def download_many(comment_links):
    loop = asyncio.get_event_loop()
    to_do = [find_href_in_comments(page) for page in sorted(comment_links)]
    wait_coro = asyncio.wait(to_do)
    res, _ = loop.run_until_complete(wait_coro)
    loop.close()
    return len(res)


def main():
    parser = parse_arguments()
    if not os.path.isdir(f'./{parser.d}'):
        os.mkdir(parser.d)
    #link_list = parse_base_page()
    comments_page_list = parse_comments_page()
    download_many(comments_page_list)
    return 0


if __name__=="__main__":
    main()
