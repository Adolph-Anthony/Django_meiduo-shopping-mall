from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from .utils import OAuthQQ
#  url(r'^qq/authorization/$', views.QQAuthURLview.as_view()),
class QQAuthURLview(APIView):
    '''
    获取QQ登录的url
    后端接口设计：
    请求方式： GET /oauth/qq/authorization/?next=xxx

    请求参数： 查询字符串

    参数名	    类型	    是否必须	说明
    next	    str	    否	    用户QQ登录成功后进入美多商城的哪个网址
    返回数据：   JSON

    {
        "login_url": "https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&client_id=101474184&redirect_uri=http%3A%2F%2Fwww.meiduo.site%3A8080%2Foauth_callback.html&state=%2F&scope=get_user_info"
    }
    '''
    def get(self,request):

        # 获取next参数
        next = request.query_params.get("next")

        # 拼接QQ登录网络
        oauth_qq = OAuthQQ(state=next)
        login_url = oauth_qq.get_qq_login_url()

        # 返回
        return Response({'login_url':login_url})



