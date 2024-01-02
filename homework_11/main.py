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
    data = bs_page.find_all('a', string=re.compile('comments'))
    result_comment = [BASE_URL + x.get('href') for x in data[1:]]
    return result, result_comment


def find_href_in_comments(comments_pages):
    global link_list
    for page in comments_pages:
        response = requests.get(page)
        bs_page = BeautifulSoup(response.text, 'lxml')
        data = bs_page.find_all('div', class_='comment')
        result = [x.find('a').get('href') for x in data \
            if x.find('a') and 'https' in x.find('a').get('href')]
        if result:
            link_list += result

# async def find_href_in_comments(comments_page):
#     global link_list
#     async with aiohttp.ClientSession() as session:
#         response = await session.request('GET', comments_page)
#         page = await response.read()
#         bs_page = BeautifulSoup(page, 'lxml')
#         data = bs_page.find_all('div', class_='comment')
#         result = [x.find('a').get('href') for x in data \
#             if x.find('a') and 'https' in x.find('a').get('href')]
#         if result:
#             link_list += result
#     return result


def download_pages(news_dict):
    pass


async def main():
    parser = parse_arguments()
    if not os.path.isdir(f'./{parser.d}'):
        os.mkdir(parser.d)
    link_list, comments_page_list = parse_base_page()
    find_href_in_comments(comments_page_list)
    for i in link_list:
        if i not in news_dict:
            news_dict[i] = False
    print(news_dict)
    return 0


if __name__=="__main__":
    asyncio.run(main())
