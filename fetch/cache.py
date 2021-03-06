import json
import re

import redis
from bs4 import BeautifulSoup

from config.configuration import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from fetch.BaiduCrawler import BaiduCrawler
from fetch.BingCrawler import BingCrawler
from fetch.SoCrawler import SoCrawler
from fetch.parse import NovelParse
from fetch.utils import get_random_user_agent, target_fetch, get_html_by_requests, extract_pre_next_chapter


async def cache_search_keyword(keyword, blacklist, allow):
    """
    对搜索功能进行缓存
    这里采用List数据类型来存储搜索结果
    :param keyword:
    :param blacklist:
    :param allow:
    :return:
    """
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASSWORD)
    baidu = BaiduCrawler()
    bing = BingCrawler()
    so = SoCrawler()
    # todo 这里需要花费两秒钟读取数据
    length = redis_client.llen(keyword)
    if length == 0:
        # 缓存搜索结果
        results = await baidu.search(keyword=keyword, blacklist=blacklist, allow=allow) + \
                  await bing.search(keyword=keyword, blacklist=blacklist, allow=allow) + \
                  await so.search(keyword=keyword, blacklist=blacklist, allow=allow)
        for index, item in enumerate(results):
            redis_client.set(keyword + ":" + str(index), json.dumps(item))
            redis_client.lpush(keyword, keyword + ":" + str(index))
            redis_client.expire(keyword + ":" + str(index), 60 * 60 * 24)
            redis_client.expire(keyword, 60 * 60 * 24)
    else:
        indexes = redis_client.lrange(keyword, 0, -1)
        results = []
        for index in indexes:
            result = json.loads(redis_client.get(index))
            results.append(result)
    results = sorted(results, key=lambda keys: keys['parsed'], reverse=True)
    return results


async def cache_novel_chapter(url, choice, chapter_tag, chapter_value):
    """
    缓存小说目录以及介绍
    这里采用String数据类型来存储章节等信息
    :param chapter_value:
    :param chapter_tag:
    :param choice:
    :param url: 源地址
    :return: 小说目录以及摘要
    """
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=1, password=REDIS_PASSWORD)
    if redis_client.get(url) is None:
        # 对拿到的html进一步解析
        headers = {
            "user-agent": await get_random_user_agent()
        }
        html = await target_fetch(url=url, headers=headers)
        novel = {}
        if not html:
            html = get_html_by_requests(url=url, headers=headers)
        if html:
            soup = BeautifulSoup(html, 'html5lib')
            parser = NovelParse(novel=novel, rule=choice, url=url)
            if chapter_tag == "id":
                content = soup.find_all(id=chapter_value)
                novel = parser.parse_id_chapter_list(content=content)
            elif chapter_tag == "class":
                # 若需要解析的内容包含在含有class属性的div中
                # 根据定义的解析规则获取符合条件的div
                content = soup.find_all(class_=chapter_value)
                novel = parser.parse_biquge(content=content)
            else:
                content = soup.find_all(chapter_value)
                # todo
            redis_client.set(url, json.dumps(novel))
            redis_client.expire(url, 60 * 60 * 24)
            return novel if content else None
        return None
    else:
        return json.loads(redis_client.get(url))


async def cache_novel_content(url, content_tag, content_value):
    """
    缓存每章节内容
    :param content_tag:
    :param content_value:
    :param url: 源地址
    :return: 每章节内容以及上下文链接
    这里采用String数据类型来存储章节等信息
    """
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=2, password=REDIS_PASSWORD)
    if redis_client.get(url) is None:
        headers = {
            "user-agent": await get_random_user_agent()
        }
        novel = {}
        html = await target_fetch(headers=headers, url=url)
        if not html:
            html = get_html_by_requests(url=url, headers=headers)
        if html:
            soup = BeautifulSoup(html, 'html5lib')
            if content_tag == "id":
                content = soup.find_all(id=content_value)
                for item in content:
                    article = item.get_text(strip=False).split("\xa0")
                    article = [i for i in article if i is not ""]
                    novel["article"] = article
            elif content_tag == "class":
                content = soup.find_all(class_=content_value)
                # todo
            else:
                # todo
                content = soup.find_all(content_value)
            # 提取出真正的章节标题
            title_reg = r'(第?\s*[一二两三四五六七八九十○零百千万亿0-9１２３４５６７８９０]{1,6}\s*[章回卷节折篇幕集]\s*.*?)[_,-]'
            title = soup.title.string
            extract_title = re.findall(title_reg, title, re.I)
            if extract_title:
                title = extract_title[0]
            else:
                title = soup.select('h1')[0].get_text()
            novel["title"] = title
            next_chapter = extract_pre_next_chapter(chapter_url=url, html=str(soup))
            novel["pages"] = []
            for key, value in next_chapter.items():
                novel["pages"].append({
                    "name": key,
                    "href": value,
                })
            redis_client.set(url, json.dumps(novel))
            redis_client.expire(url, 60 * 60 * 24)
            return novel if content else None
        return None
    else:
        return json.loads(redis_client.get(url))
