from django.shortcuts import render
from rest_framework import request
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from .utils import OAuthQQ
#  url(r'^qq/authorization/$', views.QQAuthURLview.as_view()),

from .exceptions import OAuthQQAPIError
from .models import OAuthQQUser
from .serializers import OAuthQQUserSerializer
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



class QQAuthUserView(CreateAPIView):
    """
    获取QQ登录的用户的身份信息  ?code=xxxx
    请求方式 ： GET /oauth/qq/user/?code=xxx

    请求参数： 查询字符串参数

    参数	    类型	    是否必传	说明
    code	str	    是	    qq返回的授权凭证code
    """
    serializer_class = OAuthQQUserSerializer


    def get(self,request):
        #     返回openid 查看是否绑定
        # 获取 code ,就一个不使用序列化了
        code = request.query_params.get('code')

        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        # 凭借 code 获取 access_token
        oauth_qq = OAuthQQ()
        try:
            access_token = oauth_qq.get_access_token(code)

            # 凭借 access_token 获取 openid
            openid = oauth_qq.get_openid(access_token)
        except OAuthQQAPIError:
            return Response({'message':'访问QQ接口异常'},status=status.HTTP_503_SERVICE_UNAVAILABLE)

        try:
            # 根据openid查询数据库OAuthQQUser  判断数据是否存在

            oauth_qq_user = OAuthQQUser.objects.get(openid = openid)

        except OAuthQQUser.DoesNotExist:
            # 如果数据不存在,处理open
            access_token = oauth_qq.generate_bind_user_access_token(openid)
            return Response({'access_token': access_token})
        else:
            #  如果数据存在,表示用户以及绑定过身份,签发jwt token
            # jwt签发
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            user = oauth_qq_user.user
            # 将当前的用户信息放入载荷
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            return Response({
                'username':user.username,
                'user_id':user.id,
                'token':token
            })
    # 因为是CreateAPIView视图不需要写post
    # def post(self,request):
    #     # 获取数据
    #
    #     # 校验数据
    #
    #     # 判断用户是否存在
    #
    #     # 如果存在,绑定,创建OAuthQQUser数据库数据
    #
    #     # 如果不存在,创建User,创建OAuthQQUser数据库数据
    #
    #     # 签发jwt
    #     pass

