from django.shortcuts import render
from rest_framework.generics import  CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

# Create your views here.

# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
from users.serializers import CreateUserSerializer


class UsernameCountView(APIView):
    '''请求方式： GET usernames/(?P<username>\w{5,20})/count/

        请求参数： 路径参数

        参数	        类型	    是否必传	说明
        username	str	    是	    用户名
        返回数据： JSON

        {
            "username": "itcast",
            "count": "1"
        }

        返回值	    类型	    是否必须	说明
        username	str	    是	    用户名
        count	    int	    是	    数量
        '''
    """
    用户名数量
    """
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)

# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """
    后端接口设计：
    请求方式： GET mobiles/(?P<mobile>1[3-9]\d{9})/count

    请求参数： 路径参数

    参数	    类型	是否必须	说明
    mobile	str	是	    手机号
    返回数据： JSON

    {
        "mobile": "18512345678",
        "count": 0
    }
    返回值	类型	是否必须	说明
    mobile	str	是	    手机号
    count	int	是	    数量
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)





class UserView(CreateAPIView):
    '''
    用户注册
    传入参数
    请求方式： POST /users/

    请求参数： JSON 或 表单

    参数名	    类型	是否必须	说明
    username	str	是	    用户名
    password	str	是	    密码
    password2	str	是	    确认密码
    sms_code	str	是	    短信验证码
    mobile	    str	是	    手机号
    allow	    str	是	    是否同意用户协议
    返回数据： JSON

    {
        "id": 9,
        "username": "python8",
        "mobile": "18512345678",
    }
    返回值	    类型	    是否必须	说明
    id	        int	    是	    用户id
    username	str	    是	    用户名
    mobile	    str	    是	    手机号
    '''
    serializer_class = CreateUserSerializer
