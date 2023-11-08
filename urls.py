from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import zabbix_post, zabbix_deal_data




urlpatterns = [
    path('zab/', zabbix_post, name='zabs'),
    path('zab_data/', zabbix_deal_data, name='zab_datas'),


]



