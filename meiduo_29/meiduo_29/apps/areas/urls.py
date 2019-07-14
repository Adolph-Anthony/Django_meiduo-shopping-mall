from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from . import views
urlpatterns=[
]
# 提供默认的根路由
router = DefaultRouter()
router.register('areas',views.AreasViewSet,base_name = "areas" )
urlpatterns += router.urls


# /areas/ {'get':'list'}  只返回顶级数据  parent = None
# /areas/<pk> {'get':'retrieve'}