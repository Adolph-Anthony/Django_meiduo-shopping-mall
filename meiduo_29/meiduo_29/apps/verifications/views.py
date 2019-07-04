from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from meiduo_29.libs.captcha.captcha import captcha
from django_redis import get_redis_connection

from verifications import constants


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

        # 返回图片
        return HttpResponse(image,content_type="image/jpg")