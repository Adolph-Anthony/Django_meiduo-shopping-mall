from django_redis import get_redis_connection
from rest_framework import serializers

from oauth.models import OAuthQQUser
from users.models import User
from .utils import Oa, OAuthQQ


class OAuthQQUserSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField(label='操作凭证',write_only=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    token = serializers.CharField(read_only=True)
    sms_code = serializers.CharField(label='短信验证码',write_only=True)

    class Meta:
        Model = User
        fields = ('mobile','password','sms_code','access_token','token','id','username','token')
        extra_kwargs = {
            'username':{
                'read_only':True
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
        }
        }
    # 校验数据
    def validate(self, attrs):
        # 检验access_token
        access_token = attrs['access_token']
        openid = OAuthQQ.check_bind_user_access_token(access_token)
        if not openid:
            raise serializers.ValidationError('无效的access_token')
        # 增加 openid 属性
        attrs['openid'] = openid

        # 检验短信验证码
        mobile = attrs['mobile']
        sms_code = attrs['sms_code']
        # 连接redis  verify_codes数据库
        redis_conn = get_redis_connection('verify_codes')
        real_sms_code = redis_conn.get('sms_%s' % mobile)
        if real_sms_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码错误')

        # 如果用户存在，检查用户密码
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            password = attrs['password']
            if not user.check_password(password):
                raise serializers.ValidationError('密码错误')
            attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.get('user')
        if not user:
            # 如果不存在,创建User,创建OAuthQQUser数据库数据
            user = User.objects.create_user(
                username=validated_data['mobile'],
                password=validated_data['password'],
                mobile=validated_data['mobile'],
            )
        # 如果存在,绑定,创建OAuthQQUser数据库数据
        OAuthQQUser.objects.create(
            openid=validated_data['openid'],
            user=user
        )
        return user
