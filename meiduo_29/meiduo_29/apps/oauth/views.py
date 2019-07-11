

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
    """
    获取QQ登录的url
    """
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
    QQ登录的用户
    """
    serializer_class = OAuthQQUserSerializer
    def get(self,request):
        #获取code
        code=request.query_params.get('code')
        if not code:
            return Response({'mesage':'缺少coe'},status=status.HTTP_400_BAD_REQUEST)
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
            # print(1)
        except OAuthQQUser.DoesNotExist:
            #如果数据不存在，处理poenid　并返回
            # print(2)
            access_token=oauth_qq.generate_bind_access_token(openid)
            return Response({'access_token':access_token})
        else:
            #如果数据存在，表示用户已经绑定过身份，签发JWT token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            user=oauth_qq_user.user
            # print(3)
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