from rest_framework import status
from rest_framework.response import Response
from celery_tasks.main import celery_app
from  .untils.yuntongxun.sms import CCP
import logging

# 需要告诉logger  django 有关的配置信息
logger = logging.getLogger('django')

@celery_app.task(name='send_sms_code')
def send_sms_code(mobile,sms_code,expires,temp_id ):
    '''发送短信验证码'''
    try:
        ccp = CCP()
        # 参数 手机号 [短信验证码,有效期] 短信模版
        print('短信验证码:%s'%sms_code)
        result = ccp.send_template_sms(mobile, [sms_code, expires], temp_id)
    except Exception as e:
        logger.error('短信发送[异常][mobile:%s,message:%s]' % (mobile, e))
    else:
        if result == 0:
            logger.info('短信发送[正常][mobile:%s]' % (mobile))

        else:
            logger.warning('短信发送[失败][mobile:%s]' % (mobile))
