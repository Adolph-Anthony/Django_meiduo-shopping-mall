from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, GenericAPIView
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from users import constants
from users import serializers
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


# get /user/
class UserDetailView(RetrieveAPIView):
    '''
    用户基本信息
    RetrieveAPIView:查询模型的实例的具体视图,自带get方法

    请求方式： GET /user/

    请求参数： 无

    返回数据： JSON

    返回值	        类型	    是否必须	说明
    id	            int	    是	    用户id
    username	    str	    是	    用户名
    mobile	        str	    是	    手机号
    email	        str	    是	    email邮箱
    email_active	bool	是	    邮箱是否通过验证

    '''
    # 指明视图使用的序列化器
    serializer_class = serializers.UserDetailSerializer
    # 当前视图权限认证,仅登录认证通过的用户才能访问
    permission_classes = [IsAuthenticated]

    def get_object(self):
        '''因为原本的get_objects因为url中没有数据
         get /users/<pk>
        拿不到单一的用户数据'''
        # 重写方法根据url返回当前请求的用户
        # 类视图对象中,通过类视图对象的属性获取request
        # 在django的请求request对象中,user属性表明当前请求的用户

        return self.request.user


# PUT /email/
class EmailView(UpdateAPIView):
    '''
    UpdateAPIView 用于更新模型实例的具体视图。
    请求方式：PUT /email/

    请求参数： JSON 或 表单

    参数	    类型	是否必须	说明
    email	str	是	    Email邮箱
    返回数据： JSON

    返回值	类型	是否必须	说明
    id	    int	是	    用户id
    email	str	是	    Email邮箱
    '''

    serializer_class = serializers.EmailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
        # def put(self):
        # 获取email
        # 校验email
        # 查询user
        # 更新数据
        # 序列化返回


# url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
class VerifyEmailView(APIView):
    """
    邮箱验证
    请求方式：GET /emails/verification/?token=xxx

    请求参数： 查询字符串参数

    参数	        类型	是否必须	说明
    token	    str	是	    用于验证邮箱的token
    返回数据： JSON

    返回值	类型	是否必须	说明
    message	str	是	    验证处理结果
    """

    def get(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})


class AddressViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    """
    serializer_class = serializers.UserAddressSerializer
    # 用户认证
    permissions = [IsAuthenticated]

    def get_queryset(self):
        # 得到查询集,默认逻辑未删除的地址信息
        # 你现在所需要的request的用户地址信息,过滤没有被逻辑删除的
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self, request, *args, **kwargs):
        """
        用户全部地址列表数据
        因为返回的参数太多不继承listModelView
        get /addresses/
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user

        # print('user.id',user.id)
        # print('user.default_address_id',user.default_address_id)
        # print('serializer.data:',serializer.data)
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        post /addresses/
        """
        # 检查用户地址数据数目不能超过上限
        count = request.user.addresses.count()
        # 如果现有的地址数目大于20条
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)
        # 校验通过之后执行继承的create方法
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        delete /addresses/<PK>
        返回204代表删除成功
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None, address_id=None):
        """
        设置默认地址
        put /addresses/<pk>/status/
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None, address_id=None):
        """
        修改标题
        put /addresses/<pk>/title/
        """
        address = self.get_object()
        serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserBrowsingHistoryView(CreateAPIView, GenericAPIView):
    """
    用户浏览历史记录
    请求方式：POST /browse_histories/

    请求参数：JSON 或 表单

    参数  	    类型	    是否必须	说明
    sku_id	    int	    是  	    商品sku编号
    返回数据：   JSON

    返回值	类型	是否必须	说明
    sku_id	int	是	    商品sku编号
    """
    # 设置序列化器
    serializer_class = serializers.AddUserBrowsingHistorySerializer
    # 权限认证
    permission_classes = [IsAuthenticated]

