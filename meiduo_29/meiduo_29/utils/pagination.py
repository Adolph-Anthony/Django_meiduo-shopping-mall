from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    '''分页参数'''
    # 默认 每页两条
    page_size = 2
    # 前端访问指明每页数量的参数
    page_size_query_param = 'page_size'
    # 限制前段最大可设置20条
    max_page_size = 20