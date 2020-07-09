from fetch.cache import cache_novel_chapter, cache_novel_content


async def get_novels_chapter(url, choice, chapter_tag, chapter_value):
    return await cache_novel_chapter(url=url, choice=choice, chapter_tag=chapter_tag, chapter_value=chapter_value)


async def get_novels_content(url, content_tag, content_value):
    return await cache_novel_content(url=url, content_tag=content_tag, content_value=content_value)
