import os
import django
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(current_dir)
sys.path.append(project_dir)
os.environ["DJANGO_SETTINGS_MODULE"] = "main.settings"
django.setup()

from zabbix_omoc.models import Bitrix_zabbix, Host_zabbix
from datetime import datetime
import json
import time 
from netmiko import ConnectHandler,NetMikoTimeoutException


olt = Host_zabbix.objects.all()

olt = olt.values()


data = {}
while 1==1:
   test1 = datetime.now()
   if test1.strftime('%H:%M') == '21:00':

         for item in olt:
            
            k = item['host_name']
            v = item['host']
            username="" # имя пользователя 	
            password="" # пароль пользователя
            port="" # порт оборудования 
            OLT = {
               'device_type': 'cisco_ios',
               'host': f'{v}',
               'username': username,
               'password': password,
               'secret': 'secret',
               'port': port,
            }
            try:
               ssh_connect = ConnectHandler(**OLT)
               output = ssh_connect.send_command('show mac address-table | exclude 1', read_timeout=120)
               abon_count = output.count('epon0/')
               olt_abon = f'{k}: {abon_count}'
               print(olt_abon)
               data[k] = abon_count
               with open('olt.json', 'w') as file:
                  json.dump(data, file, indent=1)

            except (NetMikoTimeoutException):
               n = 0
               olt_abon = f'{k}: {n}'
               data[k] = n
               print(olt_abon)
               with open('olt.json', 'w') as file:
                  json.dump(data, file, indent=1)


