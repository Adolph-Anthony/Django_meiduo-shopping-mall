from django.db import models

# Create your models here.
class Area(models.Model):
    """
    行政区划
    其实应该继承我们自定义的baseModel 但是测试数据没有包含那两个字段,所以继承基本的模型类
    """
    name = models.CharField(max_length=20, verbose_name='名称')
    # 'self' 自关联
    # on_delete 设置级联, SET_NULL 主表删除数据时 设置为NULL，仅在该字段null=True允许为null时可用
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='subs', null=True, blank=True, verbose_name='上级行政区划')

    class Meta:
        db_table = 'tb_areas'
        verbose_name = '行政区划'
        verbose_name_plural = '行政区划'

    def __str__(self):
        return self.name