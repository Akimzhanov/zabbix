from django.shortcuts import render
from .models import Bitrix_zabbix
import requests
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from datetime import datetime,date
import json, os
import logging
from bs4 import BeautifulSoup
from django.http import HttpResponse,  JsonResponse
import asyncio
from fast_bitrix24 import Bitrix,BitrixAsync
os.environ["DJANGO_SETTINGS_MODULE"] = "main.settings"
import datetime,time
from netmiko import ConnectHandler,NetmikoTimeoutException,NetmikoAuthenticationException




webhook = "" # токен с битрикс24
logging.getLogger('fast_bitrix24').addHandler(logging.StreamHandler())

 



#Создаем новую сделку для аварии
async def zabbix_deal(subject, host,severity,started, origin_id):

    webhook = "" # токен с битрикс24
    b = BitrixAsync(webhook)
    method = 'crm.deal.add' 
    test = {'fields': {
        'TYPE_ID':'SALE',
        'UF_CRM_1683862514667': subject,
        'UF_CRM_1683862249370': host,
        'UF_CRM_1683862329529': severity,
        'UF_CRM_1684229046793': started,
        'UF_CRM_1686107710317': origin_id,
        #'UF_CRM_1684468800920': count_abon,
        'CATEGORY_ID': '53'
}}
    test2 = await b.call(method, test)
    return HttpResponse(test2)

#Создаем новость в живой ленте битрикс 
async def add_livefeed_message(subject, host,severity,started):
    b = BitrixAsync(webhook)
    url = webhook + 'log.blogpost.add'
    params = {
         
            #'POST_TITLE': subject,
            'POST_MESSAGE': f'{subject}\n{host}\n{severity}\n{started}', 
            'DEST[]': 'U24675',
            'IMPORTANT': 'Y',
        
    }
 
    response = requests.post(url, data=params) 
    response_data = json.loads(response.text)
    if 'error' in response_data:
        print('Ошибка: ' + response_data['error'])
        print('Описание ошибки: ' + response_data['error_description'])
        return False
    else:
        print('Запись успешно добавлена в живую ленту!')
        test = {
    'subject': subject
}
        return HttpResponse(response)


async def timeman_status():
    a = [51, 79, 143, 2465, 2673, 38818, 41433]
    results = []
    webhook = "" # токен с битрикс24
    b = BitrixAsync(webhook)
    method = 'timeman.status'
    for i in a:
        params = {
            'USER_ID': str(i)
        }
        test = await b.call(method, params)
        if test['STATUS'] == 'OPENED':
            results.append(i) 
    return results  




async def problem(deal_id, subject,host):
    y = await timeman_status()
    webhook = "" # токен с битрикс24
    now = datetime.datetime.now()
    deadline = now + datetime.timedelta(hours=12)
    b = BitrixAsync(webhook)
    method = 'tasks.task.add'
    params = {
        'fields': {
            'UF_CRM_TASK': [f'D_{deal_id}'],
            'TITLE': f'{subject}',
            'GROUP_ID': '111',
            'DESCRIPTION': f'{host}',
            'CATEGORY_ID': '53',
            'CREATED_BY': '87',
            'RESPONSIBLE_ID': '2663', 
            'ACCOMPLICES': y,
            'DEADLINE': deadline.strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    test = await b.call(method, params, raw=True)

    return test


async def close_task(task_id):
    webhook = "" # токен с битрикс24
    b = BitrixAsync(webhook)
    method = 'tasks.task.complete'
    params = {
        'taskId': task_id
    }
    test = await b.call(method, params)
    return test

async def link_down(ip_host, subject):
    if 'High error' not in subject and 'Temperature' not in subject:
        t = []
        for i in range(17):
            if f'EPON0/{i}' in subject:
                t.append(i)
        abon_port = t[-1]
        username="root"
        password="*hjvfirf!"
        port="22"
        OLT = {
            'device_type': 'cisco_ios',
            'host': ip_host,
            'username': '',#имя пользователя 	
            'password': '',# пароль пользователя 
            'secret': 'secret',
            'port': port,
            }

        ssh_connect = ConnectHandler(**OLT)
        t = ssh_connect.send_command('terminal width 0')
        output = ssh_connect.send_command(f'show epon active-onu interface epon 0/{abon_port}', read_timeout=1600)
        line_out = output.splitlines()
        count_power = 0
        count_wire = 0
        count_know = 0
        for i in line_out:
            if 'power-off' in i:
                count_power += 1
            elif 'wire-down' in i:
                count_wire += 1
            else:
                count_know += 1
        count_all = count_know + count_power + count_wire
        if count_all == 0:
            one_percent = 0
        else:
            one_percent = 100 / count_all
        wire_percent = count_wire * one_percent
        return wire_percent



#Получаем POST данные с Zabbix
@csrf_exempt 
def zabbix_post(request):
    if request.method == 'POST':
  
        try:
            test = request.body 
            data = json.loads(request.body)

            subjects = data['subject'] 
            subject = subjects[9:]
            host = data['host'] 
            severity = data['severity'] 
            started = str(data['started']) 
            origin_id = data['origin_id'] 
            ip_host = str(data['ip_host'])
            print(ip_host)
            print('//////////////////////////////////////////////////////////////////')
            county = 0


            with open('/home/akyl/skynet/zabbix_omoc/tasks.json','r') as file:
                id_task = json.load(file)
                tasks = 0
                for i in id_task:
                    tas = str(i.keys())
                    task_id_origin = tas[12:-3]
                    if origin_id == task_id_origin:
                        task = str(i.values())
                        task_id = task[13:-2]
                        task_id = int(task_id)
                        test = asyncio.run(close_task(task_id))
                        tasks += 1
                    else:
                        pass



            with open('/home/akyl/skynet/zabbix_omoc/zabbix.json','r') as file:
                id_problem = json.load(file)
                for k, v in enumerate(id_problem):
                    if origin_id in v.keys():
                        county +=1 
                    else:
                        pass
 
            if county == 0:
               testy = None
               with open('/home/akyl/skynet/zabbix_omoc/zabbix.json','r') as file:
                  data_post = json.load(file)
                  for k, v in enumerate(data_post):
                     a = str(v.keys())
                     origin_ids = a[12:-3]
                     y = v[origin_ids]
                     u = str(y.keys())
                     host_name = u[12:-3]
                     *test, = y
                     if host in test:
                        deal_id = v[origin_ids][host_name]
                        print(deal_id)
                        if tasks != 1:
                            if 'Interface EPON0/' in subject and 'Link down' in subject:
                                try:
                                    link_down2 = asyncio.run(link_down(ip_host, subject))
                                except Exception as e:
                                    print(f"Error in running the link_down function: {e}")
                                    link_down2 = 0
                                if link_down2 >=70:
                                    testy = asyncio.run(problem(deal_id, subject, host))
                                    task_id= testy['result']['task']['id']
                                    task_id = int(task_id)
                                    with open('/home/akyl/skynet/zabbix_omoc/tasks.json','r') as file:
                                        datata = json.load(file)
                                        datata.append({origin_id: task_id})
                                    with open('/home/akyl/skynet/zabbix_omoc/tasks.json','w') as file:
                                        json.dump(datata, file, indent=1)
                                elif 'Temperature' in subject: 
                                    testy = asyncio.run(problem(deal_id, subject, host))
                                    task_id= testy['result']['task']['id']
                                    task_id = int(task_id)
                                    with open('/home/akyl/skynet/zabbix_omoc/tasks.json','r') as file:
                                        datata = json.load(file)
                                        datata.append({origin_id: task_id})
                                    with open('/home/akyl/skynet/zabbix_omoc/tasks.json','w') as file:
                                        json.dump(datata, file, indent=1)
                            else:
                                testy = asyncio.run(problem(deal_id, subject, host))
                                task_id= testy['result']['task']['id']
                                task_id = int(task_id)

                                with open('/home/akyl/skynet/zabbix_omoc/tasks.json','r') as file:
                                    datata = json.load(file)
                                    datata.append({origin_id: task_id})

                                with open('/home/akyl/skynet/zabbix_omoc/tasks.json','w') as file:
                                    json.dump(datata, file, indent=1)

                        else:
                            pass

                        break
 
                  else:
                      today = str(date.today())[5:].replace('-','.')
                      startedd = started[17:]
                      if 'High error' not in subjects and 'Resolved' not in subjects and 'Temperature' not in subjects:
                          if time.strptime(today, '%m.%d') == time.strptime(startedd,'%m.%d'):
                              if 'Interface EPON0/' in subject and 'Link down' in subject:
                                  link_down2 = asyncio.run(link_down(ip_host, subject))
                                  try:
                                      if link_down2 >=70:
                                          testy = asyncio.run(zabbix_deal(subject, host,severity,started, origin_id))
                                          t = testy
                                          deal = str(t.content)
                                          deal_id = deal[2:-1]
                                          with open('/home/akyl/skynet/zabbix_omoc/zabbix.json','r') as file:
                                              datata = json.load(file)
                                              datata.append({origin_id: {host: deal_id}})
                                          with open('/home/akyl/skynet/zabbix_omoc/zabbix.json','w') as file:
                                              json.dump(datata, file, indent=1)
                                  except TypeError:
                                    pass
                              else:
                                  testy = asyncio.run(zabbix_deal(subject, host,severity,started, origin_id))
                                  t = testy
                                  deal = str(t.content)
                                  deal_id = deal[2:-1]
                                  with open('/home/akyl/skynet/zabbix_omoc/zabbix.json','r') as file:
                                      datata = json.load(file)
                                      datata.append({origin_id: {host: deal_id}})
                                  with open('/home/akyl/skynet/zabbix_omoc/zabbix.json','w') as file:
                                      json.dump(datata, file, indent=1)
                              return HttpResponse(200)

               return HttpResponse(200)
            else:
                with open('/home/akyl/skynet/zabbix_omoc/zabbix.json','r') as file:
                    data_post = json.load(file)
                    data = []
                    for v in data_post:
                        if origin_id in v.keys():
                            e = list(v.keys())[0]
                            print(e)
                        else:
                            data.append(v)

                    with open('/home/akyl/skynet/zabbix_omoc/zabbix.json','w') as file:
                        json.dump(data, file, indent=1)




                return HttpResponse(500)

 
        
            

        except KeyError as e:
            return JsonResponse({'status': 'error', 'message': f'Missing key: {e}'}, status=400)

        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': f'Invalid JSON: {e}'}, status=400)

    else:
        return HttpResponse(500)




@csrf_exempt
def zabbix_deal_data(request):
    if request.method == 'POST':
        post_data = request.POST.copy()
        deal = post_data.get('document_id[2]')
        deal_id = str(deal)[5:]
        a = asyncio.run(zabbix_deal_datas(deal_id))




        return HttpResponse(200)

    else:

        return HttpResponse(500)

#Добавляем ID новости в сделку 
async def id_livefeed(deal_id, livefeed):
    b = BitrixAsync(webhook)
    method = 'crm.deal.update'
    params = {"id":f'{deal_id}',
                   'fields': {
           'UF_CRM_1684834780970': livefeed
}}
    test = await b.call(method, params)


#Получаем ID новости
async def zabbix_deal_datas(deal_id):
         if 5==5:
            b = BitrixAsync(webhook)
            method = 'crm.deal.get'
            params = {
             "id": f'{deal_id}',
               'fields': {


               }}
            test = await b.call(method, params)
            host = test['UF_CRM_1683862249370']
            subject = test['UF_CRM_1683862514667']
            severity = test['UF_CRM_1683862329529']
            started = test['UF_CRM_1684229046793']
            subject = subject[9:]

            a = await add_livefeed_message(subject, host,severity,started)
            livefeed = a.content.decode('utf-8')

            livefeed = livefeed[10:14]
            livefeed = int(livefeed)
            await id_livefeed(deal_id,livefeed)

            return livefeed













