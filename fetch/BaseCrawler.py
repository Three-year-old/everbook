import aiohttp
import async_timeout

from config import configuration


class BaseCrawler:
    def __init__(self):
        self.config = configuration

    async def fetch_url(self, url, params, headers):
        """
        获取搜索引擎的结果
        :param url: 搜索地址，如百度则为https://www.baidu.com/s?wd=....
        :param params: 搜索参数
        :param headers: 请求头
        :return:
        """
        with async_timeout.timeout(15):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params, headers=headers) as response:
                        assert response.status == 200
                        try:
                            text = await response.text()
                        except:
                            text = await response.read()
                        return text
            except Exception as e:
                raise e
