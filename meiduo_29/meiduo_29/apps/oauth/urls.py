from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from . import views
urlpatterns=[
 url(r'^qq/authorization/$', views.QQAuthURLview.as_view()),

]