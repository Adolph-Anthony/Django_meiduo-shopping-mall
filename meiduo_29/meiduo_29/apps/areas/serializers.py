from rest_framework import serializers
from .models import Area



class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id','name')


class SubAreaSerializer(serializers.ModelSerializer):
    # 多个值
    subs = AreaSerializer(many=True,read_only=True)

    class Meta:
        model = Area
        fields = ('id','name','subs')

    # {
    #     'id':xxx,
    #     'name':xxx,
    #     'subs':{
    #         'id':xxx,
    #         'name':xxx
    #     }
    #
    #
    #
    # }