import asyncio
import csv
from datetime import datetime
import html
import logging
import os
import re
import aiohttp
from typing import List
import async_timeout
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

PERIOD = 30
LIMIT = 30
VERBOSE = False  # `True` для уровня DEBUG
PATH = "./output"
CONNECTIONS_LIMIT = 3
LOG_FILE = "ycrawler.log"

# Шаблоны URL и константы времени ожидания
URL_TEMPLATE = "https://hacker-news.firebaseio.com/v0/item/{}.json"
STORY_URL_TEMPLATE = "https://news.ycombinator.com/item?id={}"
TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
FETCH_TIMEOUT = 30
REFERENCES_REGEXP = r'<a[^>]* href="([^"]*)"'
REPORT_FILE = "news_list.csv"

# Настройка логирования
logging.basicConfig(format="[%(asctime)s] %(levelname).1s %(message)s", datefmt="%Y.%m.%d %H:%M:%S")
logger = logging.getLogger()

# Присваиваем уровень логирования в зависимости от VERBOSE
logging_level = logging.DEBUG if VERBOSE else logging.INFO
fh = logging.FileHandler(LOG_FILE)
fh.setLevel(logging_level)
logger.addHandler(fh)
logger.setLevel(logging_level)


class URLFetcher:
    def __init__(self):
        self.fetch_counter = 0

    async def fetch(self, session, url, dest_dir=None):
        try:
            async with async_timeout.timeout(FETCH_TIMEOUT):
                self.fetch_counter += 1
                async with session.get(url) as response:
                    if dest_dir:
                        save_content_to_disk(await response.read(), url, dest_dir)
                    else:
                        return await response.json()
        except asyncio.TimeoutError:
            logger.warning(f"Запрос превысил лимит времени ожидания для: {url}")
            # здесь может быть логика повторного запроса или отмены задачи
        except asyncio.CancelledError:
            logger.info(f"Задача была отменена: {url}")
            # здесь могут быть действия по корректному закрытию ресурсов
        except Exception as e:
            logger.error(f"Ошибка при запросе {url}: {e}")
            # Обработка других исключений


# Сохранение содержимого в файл на диске
def save_content_to_disk(resp_bytes, url, dest_dir):
    filename = re.sub(r"[?:*<>,; /\\]", '', url)
    print("comment filename={0}".format(filename))
    full_filename = os.path.join(dest_dir, filename[:20])
    full_filename += ".html"
    with open(full_filename, "wb+") as f:
        f.write(resp_bytes)


# Получение пути до истории и запись в CSV
def get_path_of_story(story_dir, story_title, story_id) -> str:
    path = os.path.join(story_dir, str(story_id))
    if not os.path.exists(path):
        os.makedirs(path)
        with open(os.path.join(story_dir, REPORT_FILE), 'a+', encoding='UTF8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([story_id, story_title])
    return path


# Загрузка списка обработанных историй
def load_processed_stories_list(story_dir: str) -> List[int]:
    path_to_file = os.path.join(story_dir, REPORT_FILE)
    processed_ids = []
    if os.path.exists(path_to_file):
        with open(path_to_file, 'r', encoding='UTF8') as f:
            reader = csv.reader(f)
            for row in reader:
                processed_ids.append(int(row[0]))
    return processed_ids


# Получение страницы со ссылками и комментариями
async def get_page_with_references(session, fetcher, post_id, story_dir):
    url = URL_TEMPLATE.format(post_id)
    response = await fetcher.fetch(session, url)
    if response and response.get("type") == "story":
        await handle_story(session, fetcher, response, story_dir)
    elif response and response.get("type") == "comment":
        await handle_comment(session, fetcher, response, story_dir)


# Обработка истории
async def handle_story(session, fetcher, response, story_dir):
    story_url = response.get("url", STORY_URL_TEMPLATE.format(response["id"]))
    story_title = response.get("title", "untitled")
    story_dir = get_path_of_story(story_dir, story_title, response["id"])
    await fetcher.fetch(session, story_url, dest_dir=story_dir)


# Обработка комментария
async def handle_comment(session, fetcher, response, story_dir):
    text = html.unescape(response.get("text", ""))
    refs = set(re.findall(REFERENCES_REGEXP, text))
    tasks = [fetcher.fetch(session, comment_url, story_dir) for comment_url in refs]
    await asyncio.gather(*tasks)


# Основной метод для загрузки топ историй с комментариями
async def download_top_stories(limit, path, connections_limit):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit_per_host=connections_limit)) as session:
        fetcher = URLFetcher()
        response = await fetcher.fetch(session, TOP_STORIES_URL)
        if response:
            tasks = [get_page_with_references(session, fetcher, post_id, path) for post_id in response[:limit]]
            await asyncio.gather(*tasks)


# Периодическое выполнение задачи загрузки топ историй
async def poll_top_stories(period, limit, path, connections_limit):
    iterations = 0
    while True:
        logger.info(f"Downloading top {limit} stories (iteration {iterations})")
        start_time = datetime.now()
        await download_top_stories(limit, path, connections_limit)
        total_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Downloading took {total_time:.3f} seconds")
        logger.info(f"Waiting {period} sec...")
        await asyncio.sleep(period)

# Загрузка списка уже собранных историй
COLLECTED_STORIES = load_processed_stories_list(PATH)

logger.info(f"Ycrawler запущен с опциями: PERIOD={PERIOD}, LIMIT={LIMIT}, PATH={PATH}, CONNECTIONS_LIMIT={CONNECTIONS_LIMIT}, LOG_FILE={LOG_FILE}")
asyncio.run(poll_top_stories(PERIOD, LIMIT, PATH, CONNECTIONS_LIMIT))
