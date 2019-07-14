from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

# Create your views here.
# 第一级
# GET /areas/
from areas import serializers
from areas.models import Area


# class Areas(ListAPIView):
#     '''
#     查询Areas数据_复数
#     序列化返回
#     '''


# 继承自GenericAPIVIew，同时包括了ListModelMixin、RetrieveModelMixin。
from areas.serializers import AreaSerializer


class AreasViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    '''

    请求省份数据
    请求方式： GET /areas/
    请求参数： 无
    返回数据： JSON
    返回值	类型	是否必传	说明
    id	i   nt	是	    省份id
    name	str	是	    省份名称

    请求城市或区县数据
    请求方式: GET /areas/(?P<pk>\d+)/
    请求参数: 路径参数

    参数	类型	是否必传	说明
    pk	int	是	上级区划id（省份id用于获取城市数据，或城市id用于获取区县数据）
    返回数据： JSON
    返回值	类型	    是否必传	说明
    id	    int	    是	    上级区划id（省份id或城市id）
    name	str	    是	    上级区划的名称
    subs	list[]	是	    下属所有区划信息

    继承自GenericAPIVIew，同时包括了ListModelMixin、RetrieveModelMixin。
    只读
    查询单一数据对象
    序列化返回
    '''
    # 关闭分页处理
    pagination_class = None

    def get_queryset(self):
        if self.action == 'list':
            # 获取arent = None的全部资源
            print("1")
            return Area.objects.filter(parent = None)
        else:
            # 只获取当前<pk>存在的情况下,跟pk有关的资源
            return Area.objects.all()
    # 区分请求方式不一样时候选择的序列化器
    def get_serializer_class(self):
        if self.action =='list':
            return serializers.AreaSerializer
        else:
            return serializers.SubAreaSerializer

# /areas/ {'get':'list'}  只返回顶级数据  parent = None
# /areas/<pk> {'get':'retrieve'}
