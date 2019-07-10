import urllib
from urllib.parse import urlencode
from urllib.request import urlopen
from django.conf import settings
import logging
import json
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSerializer


from .exceptions import OAuthQQAPIError
from . import constants
logger = logging.getLogger('django')
class OAuthQQ(object):
    """
    QQ认证辅助工具类
    """
    def __init__(self, client_id=None ,client_secret=None, redirect_uri=None, state=None):
        # 如果 or 的左边不存在 就去找右边的默认值
        # 保存有关于qq应用开发信息以及返回页面
        self.client_id = client_id or settings.QQ_CLIENT_ID
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE  # 用于保存登录成功后的跳转页面路径

    def get_qq_login_url(self):
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': self.state,
            'scope': 'get_user_info',
        }

        url = 'https://graph.qq.com/oauth2.0/authorize?' + urlencode(params)

        return url

    def get_access_token(self,code):
        '''
        获取access_token
        :param code: qq提供的code
        :return: access_token
        '''
        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'redirect_uri': self.redirect_uri
        }

        url = 'https://graph.qq.com/oauth2.0/token?' + urlencode(params)
        try:
            # 发送请求
            resp = urlopen(url)
            # 读取响应体数据
            resp_data = resp.read() # bytes
            # 转换类型
            resp_data = resp_data.decode()  # str
            print('reso_data',resp_data)
            #解析access_token
            resp_dict =urllib.parse.parse_qs(resp_data)
            print('resp_dict',resp_dict)
        except Exception as e:
            logger.error('获取access_token异常%s'%e)
            raise OAuthQQAPIError
        else:
            access_token = resp_dict.get('access_token')
            return access_token

    def get_openid(self,access_token):
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token
        try:
            # 发送请求
            resp = urlopen(url)
            # 读取响应体数据
            resp_data = resp.read()  # bytes
            # 转换类型
            resp_data = resp_data.decode()  # str

            # 返回的数据 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;  json格式
            # 截取字符串
            resp_data = resp_data[10:-4]
            # 解析成字典
            resp_dict = json.loads(resp_data)
            print('第一次',resp_dict)
        except Exception as e:
            logger.error('获取openid异常%s' % e)
            raise OAuthQQAPIError
        else:
            access_token = resp_dict.get('access_token')
            return access_token

    def generate_bind_user_access_token(self,openid):
        serializer = TJWSerializer(settings.SECRET_KEY, constants.BIND_USER_ACCESS_TOKEN_EXPORES)
        # 转换格式 返回bytes类型
        token = serializer.dumps({'openid':openid})
        return token.decode()