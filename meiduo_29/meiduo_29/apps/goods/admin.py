from django.contrib import admin

# Register your models here.
from goods import models

class SKUAdmin(admin.ModelAdmin):
    '''重写系统的管理类,实现异步任务'''
    def save_model(self, request, obj, form, change):
        '''
        保存商品
        :param request: 当前视图请求对象
        :param obj: 当前数据还未保存的模型类对象
        :param form: 原始表单数据
        :param change: 是否修改了的数据
        :return:
        '''
        # 保存
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.id)

class SKUSpecificationAdmin(admin.ModelAdmin):
    '''SKU规格信息管理'''
    def save_model(self, request, obj, form, change):
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)

class SKUImageAdmin(admin.ModelAdmin):
    '''sku图像管理'''
    def save_model(self, request, obj, form, change):
        '''
        :param obj: SKUImage 对象 obj.sku
        :return:
        '''
        obj.save()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(obj.sku.id)

        # 设置SKU默认图片
        sku = obj.sku
        # 如果默认图片为空
        if not sku.default_image_url:
            sku.default_image_url = obj.image.url
            sku.save()

    def delete_model(self, request, obj):
        sku_id = obj.sku.id
        obj.delete()
        from celery_tasks.html.tasks import generate_static_sku_detail_html
        generate_static_sku_detail_html.delay(sku_id)

admin.site.register(models.GoodsCategory)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU, SKUAdmin)
admin.site.register(models.SKUSpecification, SKUSpecificationAdmin)
admin.site.register(models.SKUImage, SKUImageAdmin)