import os
import argparse
import asyncio
import aiofiles
import aiohttp
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://news.ycombinator.com/'
news_dict = {}

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, help='Название папки для сохранения страниц', default='page_download')
    parser.add_argument('-t', type=int, help='Количество секунд между запусками обкачки новостного комбинатора', default=10)
    return parser.parse_args()


def parse_base_page():
    responce = requests.get(BASE_URL)
    bs_page = BeautifulSoup(responce.text, 'lxml')
    data = bs_page.find_all('span', class_='titleline')
    result = [x.find('a').get('href') for x in data]
    return result


async def get_news_page(news):
    async with aiohttp.ClientSession() as session:
        response = await session.request('GET', news)
        page = await response.read()
        return page


async def download_news(news):
    if news not in news_dict.keys():
        page_news = await get_news_page(news)
        news_dict[news] = True
    return True


def main():
    parser = parse_arguments()
    if not os.path.isdir(f'./{parser.d}'):
        os.mkdir(parser.d)
    news_list = parse_base_page()
    loop = asyncio.get_event_loop()
    to_do = [download_news(x) for x in sorted(news_list)]
    wait_coro = asyncio.wait(to_do)
    result, _ = loop.run_until_complete(wait_coro)
    loop.close()
    return 0


if __name__=="__main__":
    main()
