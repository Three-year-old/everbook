from django.contrib import admin
from fetch.models import BlackDomain, Rule


@admin.register(BlackDomain)
class BlackDomainAdmin(admin.ModelAdmin):
    list_display = ['domain', ]


@admin.register(Rule)
class BlackDomainAdmin(admin.ModelAdmin):
    list_display = ['domain', 'url', 'chapter_tag', 'chapter_value', 'content_tag', 'content_value']
