from django.db import models


class BlackDomain(models.Model):
    domain = models.CharField()

    class Meta:
        db_table = 'blacklist'
        verbose_name = '黑名单'
        verbose_name_plural = verbose_name
