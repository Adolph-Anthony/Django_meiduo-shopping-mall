from django.contrib import admin

from . import models

# Register your models here.
# 管理页面渲染    广告内容类别 和 广告内容

admin.site.register(models.ContentCategory)
admin.site.register(models.Content)