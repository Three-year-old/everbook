import random
import re
from collections import OrderedDict
from urllib.parse import urlparse, urljoin

import aiohttp
import async_timeout
import cchardet
import requests
from bs4 import BeautifulSoup


async def get_random_user_agent():
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    return random.choice(user_agent_list)


def get_netloc(url):
    """
    获取netloc
    :param url:
    :return:  netloc
    """
    netloc = urlparse(url).netloc
    return netloc or None


async def target_fetch(url, headers, timeout=15):
    with async_timeout.timeout(timeout):
        try:
            async with aiohttp.ClientSession() as client:
                async with client.get(url, headers=headers) as response:
                    assert response.status == 200
                    try:
                        text = await response.text()
                    except:
                        try:
                            text = await response.read()
                        except aiohttp.ServerDisconnectedError as e:
                            text = None
                    return text
        except Exception as e:
            return None


def get_html_by_requests(url, headers, timeout=15):
    try:
        response = requests.get(url=url, headers=headers, verify=False, timeout=timeout)
        response.raise_for_status()
        content = response.content
        charset = cchardet.detect(content)
        text = content.decode(charset['encoding'])
        return text
    except Exception as e:
        return None


def novels_list(text):
    rm_list = ['后一个', '天上掉下个']
    for i in rm_list:
        if i in text:
            return False
        else:
            continue
    return True


def extract_pre_next_chapter(chapter_url, html):
    """
    获取单章节上一页下一页
    :param chapter_url:
    :param html:
    :return:
    """
    next_chapter = OrderedDict()
    try:
        # 参考https://greasyfork.org/zh-CN/scripts/292-my-novel-reader
        next_reg = r'(<a\s+.*?>.*[第上前下后][一]?[0-9]{0,6}?[页张个篇章节步].*?</a>)'
        judge_reg = r'[第上前下后][一]?[0-9]{0,6}?[页张个篇章节步]'
        # 这里同样需要利用bs再次解析
        next_res = re.findall(next_reg, html.replace('<<', '').replace('>>', ''), re.I)
        str_next_res = '\n'.join(next_res)
        next_res_soup = BeautifulSoup(str_next_res, 'html5lib')
        for link in next_res_soup.find_all('a'):
            text = link.text or ''
            text = text.replace(' ', '')
            if novels_list(text):
                is_next = re.search(judge_reg, text)
                if is_next:
                    url = urljoin(chapter_url, link.get('href')) or ''
                    next_chapter[text[:5]] = url
        return next_chapter
    except Exception as e:
        return next_chapter
