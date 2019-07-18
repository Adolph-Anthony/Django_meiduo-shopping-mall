from rest_framework.serializers import ModelSerializer

from goods.models import SKU


class SKUSerializer(ModelSerializer):
    class Meta:
        model = SKU
        fields =('id','name','price','default_image_url','comments')
