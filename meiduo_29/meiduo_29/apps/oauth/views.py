

# Create your views here.
#  url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from oauth.utils import OAuthQQ
from .exceptions import OAuthQQAPIError
from .models import OAuthQQUser
from .serializers import OAuthQQUserSerializer
class QQAuthURLView(APIView):
    '''
       获取QQ登录的url	    获取QQ登录的url
       后端接口设计：	    """
       请求方式： GET /oauth/qq/authorization/?next=xxx	    def get(self, request):

       请求参数： 查询字符串
       参数名	    类型	    是否必须	说明
       next	        str	    否	    用户QQ登录成功后进入美多商城的哪个网址
       返回数据：    JSON
        {
           "login_url": "https://graph.qq.com/oauth2.0/show?which=Login&display=pc&response_type=code&client_id=101474184&redirect_uri=http%3A%2F%2Fwww.meiduo.site%3A8080%2Foauth_callback.html&state=%2F&scope=get_user_info"
       }
       '''
    def get(self, request):
        """
        提供用于qq登录的url
        """
        # 获取next参数
        next = request.query_params.get('next')
        # 拼接qq登陆的网址
        oauth_qq = OAuthQQ(state=next)
        login_url = oauth_qq.get_qq_login_url()
        # 返回
        return Response({'login_url': login_url})

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
        #获取code
        code=request.query_params.get('code')
        if not code:
            return Response({'message':'缺少code'},status=status.HTTP_400_BAD_REQUEST)
        #凭借code　获取access_token
        oauth_qq=OAuthQQ()
        try:
            access_token=oauth_qq.get_access_token(code)
            # 凭借access_token 获取openid
            openid = oauth_qq.get_openid(access_token)
            # print(openid)
        except OAuthQQAPIError:
            return Response({'message':'访问qq接口异常'},status=status.HTTP_503_SERVICE_UNAVAILABLE)

        #根据openid查询上数据库OAuthQQUser 判断数据是否存在
        try:
            oauth_qq_user=OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            #如果数据不存在，处理openid　并返回
            access_token=oauth_qq.generate_bind_access_token(openid)
            return Response({'access_token':access_token})
        else:
            #如果数据存在，表示用户已经绑定过身份，签发JWT token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            user=oauth_qq_user.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            return Response({
                'username':user.username,
                'user_id':user.id,
                'token':token
            })

    # def post(self,request):
    #     # 获取数据
    #     # 校验数据
    #     # 判断用户是否存在
    #     # 如果存在，绑定　创建OAuthQQUser数据
    #     # 如果不存在,先创建User,创建OAuthQQUser数据
    #     # 签发JWT_token