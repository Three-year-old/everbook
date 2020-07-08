import asyncio
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup

from fetch.BaseCrawler import BaseCrawler
from fetch.utils import get_random_user_agent


async def data_extraction(html, blacklist, allow):
    """
    获取360搜索的结果
    :param html:
    :param blacklist: 若搜索结果在这些域名列表里则过滤
    :param allow: 已经制定解析规则的域名列表
    :return:
    """
    try:
        try:
            title = html.select('h3 a')[0].get_text()
            url = html.select('h3 a')[0].get('href', None)
        except Exception as e:
            return None

        # 针对不同的请进行url的提取
        if "www.so.com/link?m=" in url:
            url = html.select('h3 a')[0].get('data-mdurl', None)
        if "www.so.com/link?url=" in url:
            url = parse_qs(urlparse(url).query).get('url', None)
            url = url[0] if url else None

        netloc = urlparse(url).netloc
        if not url or 'baidu' in url or 'baike.so.com' in url or netloc in blacklist:
            return None
        is_parse = True if netloc in allow else False
        return {'title': title,
                'url': url.replace('index.html', '').replace('Index.html', ''),
                'is_parse': is_parse,
                'netloc': netloc}
    except Exception as e:
        return None


class SoCrawler(BaseCrawler):

    def __init__(self):
        super(SoCrawler, self).__init__()

    async def search(self, keyword, blacklist, allow):
        url = self.config.SO_URL

        headers = {
            'User-Agent': await get_random_user_agent(),
            'Referer': "http://www.so.com/haosou.html?src=home"
        }
        params = {'ie': 'utf-8', 'src': 'noscript_home', 'shb': 1, 'q': keyword, }
        html = await self.fetch_url(url=url, params=params, headers=headers)
        if html:
            soup = BeautifulSoup(html, 'html5lib')
            result = soup.find_all(class_='res-list')
            extra_tasks = [data_extraction(html=i, blacklist=blacklist, allow=allow) for i in result]
            tasks = [asyncio.ensure_future(i) for i in extra_tasks]
            done_list, pending_list = await asyncio.wait(tasks)
            results = [task.result() for task in done_list if task.result()]
            return results
        else:
            return []
