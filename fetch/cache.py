import json
import time

from fetch.BaiduCrawler import BaiduCrawler
from fetch.BingCrawler import BingCrawler
from fetch.SoCrawler import SoCrawler
import redis


async def cache_search_keyword(keyword, blacklist, allow):
    """
    对搜索功能进行缓存
    :param keyword:
    :param blacklist:
    :param allow:
    :return:
    """
    redis_client = redis.Redis(host="localhost", port=6379, db=0, password="songjie")
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
    else:
        indexes = redis_client.lrange(keyword, 0, -1)
        results = []
        for index in indexes:
            result = json.loads(redis_client.get(index))
            results.append(result)
    results = sorted(results, key=lambda keys: keys['parsed'], reverse=True)
    return results
