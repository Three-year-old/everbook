import asyncio

import aiohttp
import async_timeout
from bs4 import BeautifulSoup

from .BaseCrawler import BaseCrawler
from fetch.utils import get_random_user_agent, get_netloc
from django.conf import settings


class BaiduCrawler(BaseCrawler):
    def __init__(self):
        super(BaiduCrawler, self).__init__()

    async def search(self, keyword):
        url = settings.BAIDU_PC_URL
        params = {
            "wd": keyword,
            "ie": "utf-8",
            "rn": settings.BAIDU_RN,
            "vf_b1": 1,
            "usm": 3,
            "rsv_idx": 2,
            "rsv_page": 1
        }
        headers = {
            "user-agent": await get_random_user_agent(),
        }
        html = await self.fetch_url(url=url, params=params, headers=headers)
        if html:
            soup = BeautifulSoup(html, 'html5lib')
            result = soup.find_all(class_='result')
            extra_tasks = [self.data_extraction(html=i) for i in result]
            tasks = [asyncio.ensure_future(i) for i in extra_tasks]
            done_list, pending_list = await asyncio.wait(tasks)
            results = [task.result() for task in done_list if task.result()]
            return results
        else:
            return []

    async def data_extraction(self, html):
        try:
            url = html.select('h3.t a')[0].get('href', None)
            real_url = await self.get_real_url(url=url) if url else None
            if real_url:
                real_str_url = str(real_url)
                netloc = get_netloc(real_str_url)
                if "http://" + netloc + "/" == real_str_url:
                    return None
                if 'baidu' in real_str_url or netloc in self.black_domain:
                    return None
                title = html.select('h3.t a')[0].get_text()
                return {
                    "title": title,
                    'url': real_str_url.replace('index.html', ''),
                    'netloc': netloc
                }
            else:
                return None
        except Exception as e:
            raise e

    async def get_real_url(self, url):
        """
        获取百度搜索结果真实url
        :param url:
        :return:
        """
        with async_timeout.timeout(5):
            try:
                async with aiohttp.ClientSession() as client:
                    headers = {'user-agent': await get_random_user_agent()}
                    async with client.head(url, headers=headers, allow_redirects=True) as response:
                        url = response.url if response.url else None
                        return url
            except Exception as e:
                raise e

