import asyncio

import aiohttp
import async_timeout
from bs4 import BeautifulSoup

from fetch.BaseCrawler import BaseCrawler
from fetch.utils import get_random_user_agent, get_netloc


async def get_real_url(url):
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
        except Exception:
            return None


async def data_extraction(html, blacklist, allow):
    """
    获取百度搜索的结果
    :param html:
    :param blacklist: 若搜索结果在这些域名列表里则过滤
    :param allow: 已经制定解析规则的域名列表
    :return:
    """
    try:
        url = html.select('h3.t a')[0].get('href', None)
        real_url = await get_real_url(url=url) if url else None
        if real_url:
            real_str_url = str(real_url)
            netloc = get_netloc(real_str_url)
            if netloc not in allow:
                # 未解析的地址
                parsed = False
            else:
                # 已解析的地址
                parsed = True
            if "http://" + netloc + "/" == real_str_url:
                return None
            if 'baidu' in real_str_url or netloc in blacklist:
                return None
            title = html.select('h3.t a')[0].get_text()
            return {
                "title": title,
                "url": real_str_url.replace('index.html', ''),
                "netloc": netloc,
                "parsed": parsed,
            }
        else:
            return None
    except Exception as e:
        raise e


class BaiduCrawler(BaseCrawler):
    def __init__(self):
        super(BaiduCrawler, self).__init__()

    async def search(self, keyword, blacklist, allow):
        url = self.config.BAIDU_PC_URL
        params = {
            "wd": keyword,
            "ie": "utf-8",
            "rn": self.config.BAIDU_RN,
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
            extra_tasks = [data_extraction(html=i, blacklist=blacklist, allow=allow) for i in result]
            tasks = [asyncio.ensure_future(i) for i in extra_tasks]
            done_list, pending_list = await asyncio.wait(tasks)
            results = [task.result() for task in done_list if task.result()]
            return results
        else:
            return []

