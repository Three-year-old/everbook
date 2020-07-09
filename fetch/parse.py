from urllib.parse import urlparse


class NovelParse:
    """
    小说解析类，针对不同类型的网站进行解析
    """

    def __init__(self, novel, rule, url):
        self.novel = novel
        self.rule = rule
        self.url = url

    def parse_biquge(self, content):
        """
        目前笔趣阁是一种通用的网站，以笔趣阁系列网站为代表，主要特点表现为
        <div class="box_con”></div>有两个，第一个div中主要包含小说简介，第二个div中包含目录
        第一个div中小说基本信息又包含在id为maininfo的div中
        <div id="maininfo">
            <div id="info"></div>
            <div id="intro"></div>
        </div>
        """
        for item in content:
            # 提取小说摘要
            if item.find(id="maininfo"):
                info = item.find(id="info").text.split("\n")
                info = [i.replace("\xa0", "") for i in info if i is not ""]
                self.novel["info"] = info
                intro = []
                for j in item.find(id="intro").select("p"):
                    intro.append(j.text)
                self.novel["intro"] = intro
            # 提取小说目录
            if item.find(id="list"):
                chapter = []
                for j in item.select("dd"):
                    if self.rule == 0:
                        chapter.append({
                            "name": j.text,
                            "href": self.url + j.a["href"],
                        })
                    if self.rule == 1:
                        chapter.append({
                            "name": j.text,
                            "href": j.a["href"],
                        })
                    if self.rule == 2:
                        chapter.append({
                            "name": j.text,
                            "href": '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(self.url)) + j.a["href"],
                        })
                self.novel["chapter"] = chapter
        return self.novel

    def parse_id_chapter_list(self, content):
        """
        解析目录包含在id为chapter_list的div标签中的小说
        这种不包括小说的介绍只有章节目录
        :param content:
        :return:
        """
        info = []
        intro = []
        chapter = []
        if self.rule == 0:
            for items in content:
                for item in items.find_all(class_="chapter_list_chapterx"):
                    chapter.append({
                        "name": item.text,
                        "href": self.url + item.a["href"],
                    })
        if self.rule == 1:
            for items in content:
                for item in items.find_all(class_="chapter_list_chapterx"):
                    chapter.append({
                        "name": item.text,
                        "href": item.a["href"],
                    })
        if self.rule == 2:
            for items in content:
                for item in items.find_all(class_="chapter_list_chapterx"):
                    chapter.append({
                        "name": item.text,
                        "href": '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(self.url)) + item.a["href"],
                    })
        self.novel["info"] = info
        self.novel["intro"] = intro
        self.novel["chapter"] = chapter
        return self.novel
