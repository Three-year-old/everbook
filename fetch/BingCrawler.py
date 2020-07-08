import asyncio
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from fetch.BaseCrawler import BaseCrawler
from fetch.utils import get_random_user_agent


async def data_extraction(html, blacklist, allow):
    """
    获取必应搜索的结果
    :param html:
    :param blacklist: 若搜索结果在这些域名列表里则过滤
    :param allow: 已经制定解析规则的域名列表
    :return:
    """
    try:
        title = html.select('h2 a')[0].get_text()
        url = html.select('h2 a')[0].get('href', None)
        netloc = urlparse(url).netloc
        url = url.replace('index.html', '').replace('Index.html', '')
        if not url or 'baidu' in url or 'baike.so.com' in url or netloc in blacklist or '.html' in url:
            return None
        is_parse = True if netloc in allow else False
        return {'title': title,
                'url': url,
                'parsed': is_parse,
                'netloc': netloc}
    except Exception as e:
        return None


class BingCrawler(BaseCrawler):

    def __init__(self):
        super(BingCrawler, self).__init__()

    async def search(self, keyword, blacklist, allow):
        url = self.config.BY_URL
        headers = {
            'user-agent': await get_random_user_agent(),
            'referer': "https://www.bing.com/"
        }
        params = {'q': keyword, 'ensearch': 0}
        html = await self.fetch_url(url=url, params=params, headers=headers)
        if html:
            soup = BeautifulSoup(html, 'html5lib')
            result = soup.find_all(class_='b_algo')
            extra_tasks = [data_extraction(html=i, blacklist=blacklist, allow=allow) for i in result]
            tasks = [asyncio.ensure_future(i) for i in extra_tasks]
            done_list, pending_list = await asyncio.wait(tasks)
            results = [task.result() for task in done_list if task.result()]
            return results
        else:
            return []
