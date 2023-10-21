import json
import requests
import easygui

with open("configuration.json", 'r') as file:
    json_data= file.read()
json_data1 = json.loads(json_data)
zone_identifier = json_data1['underlying']['zone_identifier'] #区域ID

url = "https://api.cloudflare.com/client/v4/zones/%s/dns_records"%(zone_identifier)

payload={}
headers = {
   'X-Auth-Email': '17737475682@163.com',
   'Authorization': 'Bearer LWwQFaTZZKO3c0EHo7GYGd0AjsrxrdQWOqTb7k5N',
   'User-Agent': 'Apifox/1.0.0 (https://www.apifox.cn)',
   'Accept': '*/*',
   'Host': 'api.cloudflare.com',
   'Connection': 'keep-alive'
}

yuming = easygui.enterbox('请输入查询ID的解析名称。例如域名是xxx.cn，就输入xxx.cn。如果访问是www.xxx.cn,就输入www.xxx.cn')
response = requests.request("GET", url, headers=headers, data=payload)
r = response.json()
for i in range(len(['result'][0])):
    if yuming == r['result'][i]['name']:
        print('已查询到ID为',r['result'][i]['id'])
        print("CMD窗口选中直接单击右键复制完毕后按任意键退出...")
        input()
