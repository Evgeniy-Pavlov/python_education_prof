import os
import re
import datetime
import logging
import argparse
import asyncio
import aiofiles
import aiohttp
import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://news.ycombinator.com/'
logging.basicConfig(format="[%(asctime)s] %(levelname).1s %(message)s", datefmt="%Y.%m.%d %H:%M:%S")
logger = logging.getLogger()
news_dict = {}
link_list = []

def parse_arguments():
    """Функция парсинга аргументов. Принимается два аргумента:
    -d - аргумент для указания папки для сохранения страниц,
    -t - аргумент для указания количества секунд между запусками обкачки."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', type=str, help='Название папки для сохранения страниц', default='page_download')
    parser.add_argument('-t', type=int, help='Количество секунд между запусками обкачки новостного комбинатора', default=10)
    return parser.parse_args()


def parse_base_page():
    """Функция парсинга основной страницы новостного комбинатора. Функция возвращает кортеж со следующим содержимым:
    result - результирующая переменная содержащая список ссылок на новости с главной страницы комбинатора,
    result_comment - результирующая переменная содержащая список ссылок на комментарии к новостям, 
    в дальнейшем используется для сборка ссылок уже внутри них."""
    response = requests.get(BASE_URL)
    bs_page = BeautifulSoup(response.text, 'lxml')
    data = bs_page.find_all('span', class_='titleline')
    result = [x.find('a').get('href') for x in data]
    data = bs_page.find_all('a', string=re.compile('comments'))
    result_comment = [BASE_URL + x.get('href') for x in data[1:]]
    return result, result_comment


def find_href_in_comments(comments_pages):
    """Функция поиска ссылок в комментариях. Принимает единственный аргумент comments_pages.
    Ожидается, что это будет итерируемый объект (сейчас список), содержащий ссылки на комментарии.
    Результатом выполенния функции является сбор ссылок со страниц комментариев к новостям. 
    Новые ссылоки добавляются к уже существующей глобальной переменной link_list, сама функция
    ничего не возвращает."""
    global link_list
    for page in comments_pages:
        response = requests.get(page)
        bs_page = BeautifulSoup(response.text, 'lxml')
        data = bs_page.find_all('div', class_='comment')
        result = [x.find('a').get('href') for x in data \
            if x.find('a') and 'https' in x.find('a').get('href')]
        if result:
            link_list += result


async def download_page(link, parser):
    """Асинхронная функция загрузки содержимого страниц. Принимает в качестве аргументов два значения:
    link - ссылка на страницу (ожидается строка) и parser - объект содержащий аргументы при запуске скрипта.
    Функция ничего не возвращает, а лишь выполняет запись страниц в указанной папке."""
    global news_dict
    filename = re.sub(r"[?:*<>,; /\\]", r'', link)
    full_filename = os.path.join(parser.d, filename[:20])
    if not news_dict[link]:
        async with aiofiles.open(f'{full_filename}.html', mode='wb+') as handle:
            async with aiohttp.ClientSession() as session:
                try:
                    response = await session.request('GET', link)
                    page = await response.read()
                    await handle.write(page)
                    news_dict[link] = True
                except aiohttp.client_exceptions.InvalidURL as err:
                    logger.info(f'Ссылка {link} сейчас недоступна.')
                
    else:
        logger.info(f'Ссылка {link} уже была обработана ранее.')


async def loop_runner(parser):
    """Асинхронная функция запуска списка заданий.
    Функция ничего не возвращает, лишь выполняет запуск функций парсинга страниц и их загрузки."""
    global news_dict
    link_list, comments_page_list = parse_base_page()
    find_href_in_comments(comments_page_list)
    for i in link_list:
        if i not in news_dict:
            news_dict[i] = False
    loop = asyncio.get_running_loop()
    tasks = [loop.create_task(download_page(link, parser)) for link in news_dict.keys()]
    await asyncio.gather(*tasks, return_exceptions=False)


async def main():
    parser = parse_arguments()
    if not os.path.isdir(f'./{parser.d}'):
        os.mkdir(parser.d)
    while True:
        try:
            await loop_runner(parser)
        except OSError as err:
            logger.info(f"Возникла ошибка при попытке загрузки страницы. {err}")
        await asyncio.sleep(parser.t)
    logger.info(f'Сбор ссылок для скачивания страниц завершен. Всего найдено страниц {len(news_dict)}')


if __name__=="__main__":
    asyncio.run(main())
