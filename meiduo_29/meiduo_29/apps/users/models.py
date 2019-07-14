from django.conf import settings
from django.db import models
from django.contrib.auth.models import  AbstractUser
from itsdangerous import BadData
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer

from . import constants
# Create your models here.

class User(AbstractUser):
    """用户模型类"""
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    # 邮箱是否验证
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def generate_verify_email_url(self):
        """
        生成验证邮箱的url
        """
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        data = {'user_id': self.id, 'email': self.email}
        token = serializer.dumps(data).decode()
        verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=' + token
        return verify_url

    @staticmethod
    def check_verify_email_token(token):
        '''
        用不到用户数据使用静态方法
        校验邮箱链接
        '''
        #  解析需要使用到同样的serializer，配置一样的secret key和salt，使用loads方法来解析token。
        serializer = TJWSSerializer(settings.SECRET_KEY, expires_in=constants.VERIFY_EMAIL_TOKEN_EXPIRES)
        try:
            # 加载
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            # 没有异常接受一下这个数据
            user_id = data['user_id']
            email = data['email']

            # 查询数据库
            try:
                user = User.objects.get(id = user_id,email = email)
            except User.DoesNotExist:
                return None
            return user