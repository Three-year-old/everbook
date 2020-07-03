from django.db import models


class BlackDomain(models.Model):
    domain = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'blacklist'
        verbose_name = '黑名单'
        verbose_name_plural = verbose_name


class Rule(models.Model):
    domain = models.CharField(max_length=50)
    url = models.CharField(choices=(
        ('-1', '不解析，跳转到原本网页'),
        ('0', '表示章节网页需要当前页面url拼接'),
        ('1', '表示章节链接使用本身自带的链接，不用拼接'),
        ('2', '用域名进行拼接')
    ), max_length=10)
    # chapter_tag, content_tag表示小说章节所在的html标签
    # chapter_value, content_value表示小说章节所在的html标签的属性值
    chapter_tag = models.CharField(max_length=10)
    chapter_value = models.CharField(max_length=20)
    content_tag = models.CharField(max_length=20)
    content_value = models.CharField(max_length=20)

    class Meta:
        db_table = 'rule'
        verbose_name = '解析规则'
        verbose_name_plural = verbose_name

