import random

from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from meiduo_29.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
import logging

from verifications import constants
from verifications.serializers import ImageCodeCheckSerializer
from meiduo_29.utils.yuntongxun.sms import CCP
from celery_tasks.sms.tasks import send_sms_code
logger = logging.getLogger('django')

class ImageCodeView(APIView):
    '''
    图形验证码  不需要使用序列化器 继承APIView
    访问方式： GET /image_codes/(?P<image_code_id>[\w-]+)/

    请求参数： 路径参数

    参数	            类型	        是否必须	说明
    image_code_id	uuid字符串	是	    图片验证码编号

    返回数据：
    验证码图片
    '''
    def get(self,request,image_code_id):
        # 接收参数 校验参数  访问方式正则匹配已经实现
        # 生成验证码图片
        text,image =captcha.generate_captcha()

        # 保存真实值
        # 连接verify_code 2号redis数据库

        redis_conn = get_redis_connection('verify_code')
        # 设置有效期setex(存到redis数据库里的键名字,数据有效期,数据)
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        print("图片验证码是:%s"%text)
        # 返回图片
        return HttpResponse(image,content_type="images/jpg")


class SMSCodeView(GenericAPIView):
    '''访问方式： GET /sms_codes/(?P<mobile>1[3-9]\d{9})/?image_code_id=xxx&text=xxx

    请求参数： 路径参数与查询字符串参数

    参数	            类型	        是否必须	说明
    mobile	        str	        是	    手机号
    image_code_id	uuid字符串	是	    图片验证码编号
    text	        str	        是	    用户输入的图片验证码
    返回数据： JSON

    返回值	类型	    是否必传	说明
    message	str	    否	    OK，发送成功'''
    #声明序列化器类
    serializer_class = ImageCodeCheckSerializer

    def get(self,request,mobile):
        # 接受参数 校验参数   序列化器验证
        # request.query_params  rest自带方法 查询字符串里的所有参数
        serializer = self.get_serializer(data = request.query_params)
        #设置验证并且抛出异常
        serializer.is_valid(raise_exception = True)

        # 生成短信验证码
        sms_code = '%06d'%random.randint(0,999999)

        # 保存短信验证码 手机发送记录,
        redis_conn = get_redis_connection('verify_code')
        # redis_conn.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)/
        # redis_conn.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 使用redis管道提升数据库高并发能力
        pl = redis_conn.pipeline()
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        pl.setex("send_flag_%s" % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        # 管道存储的命令执行
        pl.execute()

        # 发送短信
        # try:
        #     ccp = CCP()
        #     #参数 手机号 [短信验证码,有效期] 短信模版
        #     expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        #     result = ccp.send_template_sms(mobile,[sms_code,expires],constants.SMS_CODE_TEMP_ID)
        #     print(sms_code)
        # except Exception as e:
        #     logger.error('短信发送[异常][mobile:%s,message:%s]'%(mobile,e))
        #     return Response({'message':'failed'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # else:
        #     if result == 0:
        #         logger.info('短信发送[正常][mobile:%s]'%(mobile))
        #         return Response({'message': 'OK'})
        #
        #     else:
        #         logger.warning('短信发送[失败][mobile:%s]'%(mobile))
        #         return Response({'message': 'failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # 使用celery发送短信
        expires = constants.SMS_CODE_REDIS_EXPIRES // 60
        send_sms_code.delay(mobile,sms_code,expires,constants.SMS_CODE_TEMP_ID)
        return Response({'message': 'OK'})

        # 返回