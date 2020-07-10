# 异步爬虫与解析规则
由于小说来源是在线解析的，因此选用异步爬虫来提升效率，并且需要指定相应的解析规则来匹配数据。

## 异步爬虫
`aiohttp`上手非常简单，安装好相关库依赖后，就可以直接使用了，官方文档里提供了最简单的例子
```python
import aiohttp
import asyncio

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'http://python.org')
        print(html)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```
使用时需要实例化`aiohttp.ClientSession()`对象，并且加入`async`、`await`关键字。

在本项目中，不同的搜索引擎爬虫都继承于一个公共爬虫，目录位置为[`BaseCrawler.py`](../fetch/BaseCrawler.py)，在这个公共爬虫里，就定义了类似上述例子中的抓取函数。

对于不同的搜索引擎，定义了不同的搜索结果提取函数`data_extraction`，在这个函数中，需要对搜索引擎的搜索结果进行提取，包括提取搜索结果的标题已经链接地址（百度搜索结果的真实链接地址经过了加密，因此需要多进行一步处理）

具体实现见[`BaiduCrawler.py`](../fetch/BaiduCrawler.py)、[`BingCrawler.py`](../fetch/BingCrawler.py)、[`SoCrawler.py`](../fetch/SoCrawler.py)