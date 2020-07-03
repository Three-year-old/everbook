import re

from bs4 import BeautifulSoup

from fetch.models import Rule
from fetch.utils import get_random_user_agent, target_fetch, get_html_by_requests, extract_pre_next_chapter
from .parse import NovelParse


async def get_novels_chapter(url, netloc):
    """
    获取小说目录以及介绍
    :param url: 源地址
    :param netloc: 域名
    :return: 小说目录以及摘要
    """
    # 由于aiohttp只提供RESTFUL API接口，需要对拿到的html进一步解析
    headers = {
        "user-agent": await get_random_user_agent()
    }
    html = await target_fetch(url=url, headers=headers)
    novel = {}
    if not html:
        html = get_html_by_requests(url=url, headers=headers)
    if html:
        soup = BeautifulSoup(html, 'html5lib')
        rule = Rule.objects.get(domain=netloc)
        parser = NovelParse(novel=novel, rule=rule.url, url=url)
        if rule.chapter_tag == 'id':
            content = soup.find_all(id=rule.chapter_value)
            # Todo: 解析章节在id标签的html
        elif rule.chapter_tag == 'class':
            # 若需要解析的内容包含在含有class属性的div中，根据定义的解析规则获取符合条件的div
            content = soup.find_all(class_=rule.chapter_value)
            novel = parser.parse_biquge(content=content)
        else:
            content = soup.find_all(rule.chapter_value)
        return novel if content else None
    return None


async def get_novels_content(url, netloc):
    """
    获取每章节内容
    :param url: 源地址
    :param netloc: 域名
    :return: 每章节内容以及上下文链接
    """
    headers = {
        "user-agent": await get_random_user_agent()
    }
    novel = {}
    html = await target_fetch(headers=headers, url=url)
    if not html:
        html = get_html_by_requests(url=url, headers=headers)
    if html:
        soup = BeautifulSoup(html, 'html5lib')
        selector = RULES[netloc].content_selector
        if selector.get('id', None):
            content = soup.find_all(id=selector['id'])
            for item in content:
                article = item.get_text(strip=False).split("\xa0")
                article = [i for i in article if i is not ""]
                novel["article"] = article
        elif selector.get('class', None):
            content = soup.find_all(class_=selector['class'])
        else:
            content = soup.find_all(selector.get('tag'))
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
        return novel if content else None
    return None
