from django.conf.urls import url
from . import views
urlpatterns = {
    url(r'^image_codes/(?P<image_code_id>[\w-]+)/$',views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
}