import os
import requests
import ping3
import time
import json
import sys

#读取本地文件方法
def jsonfile(file):
    with open(file, 'r') as file:
        return file.read()

def ping_ip(ip,pingTime):
    avg_delay = 0
    for _ in range(pingTime):
        start_time = time.time()  # 获取开始时间
        result = ping3.ping(ip)  # ping IP
        end_time = time.time()  # 获取结束时间

        # 计算延迟
        delay = (end_time - start_time) * 1000  # 单位：毫秒

        avg_delay += delay

    avg_delay /= pingTime  # 计算平均延迟
    return avg_delay, result, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 添加当前日期和时间


#IP拔测
def filewrit(num):
    # 定义变量
    num = num

    # 将变量存入文件
    with open('data.txt', 'a') as f:
        f.write(str(num) + '\n')

        # 读取文件并转换为数组
    arr = []
    with open('data.txt', 'r') as f:
        arr = [int(line.strip()) for line in f]

        # 打印数组
    return arr

#检测APIKEY可用性
def APIusability(Authorization):
    url = "https://api.cloudflare.com/client/v4/user/tokens/verify"

    payload = {}
    headers = {
        'Authorization': Authorization,
        'User-Agent': 'Apifox/1.0.0 (https://www.apifox.cn)',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'api.cloudflare.com',
        'Connection': 'keep-alive',
        'Cookie': '__cflb=0H28vgHxwvgAQtjUGUFqYFDiSDreGJnV2fXoho84Mph; __cfruid=d373d9b8e8ff0aecfe46e49febe6df497145554a-1697851588'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()
# 更新DNS记录
def Update_DNS(DNStype, DNScontent, DNSname, DNSproxied):
    url = "https://api.cloudflare.com/client/v4/zones/%s/dns_records/%s" % (zone_identifier, identifier)
    payload = json.dumps({
        "type": DNStype,
        "content": DNScontent,
        "name": DNSname,
        "proxied": DNSproxied
    })
    headers = {
        'X-Auth-Email': Email,
        'Authorization': Authorization,
        'User-Agent': 'Apifox/1.0.0 (https://www.apifox.cn)',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Host': 'api.cloudflare.com',
        'Connection': 'keep-alive',
        'Cookie': '__cflb=0H28vgHxwvgAQtjUGUFqYFDiSDreGJnUrBRRkuhbKHF; __cfruid=d6c8c186fda208a0c505f0f87377aa6041715c75-1697797940'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)
    r = response.json()
    if r['errors'] != []:
        print("ERROR：请求变更DNS时出现错误")
        print(r['errors'])

#读取配置文件内容
json_data = jsonfile("configuration.json")
json_data1 = json.loads(json_data)
zone_identifier = json_data1['underlying']['zone_identifier'] #区域ID
identifier = json_data1['underlying']['identifier'] #DNS记录ID
Email = json_data1['underlying']['Email'] #域邮箱
Authorization = json_data1['underlying']['Authorization'] #账户APIKEY
Time = json_data1['underlying']['Time']
pollTime = json_data1['underlying']['pollTime']
IP = json_data1['underlying']['IP']
pingTime = json_data1['underlying']['pingTime']
overtime = json_data1['underlying']['overtime']

DNStype1 = json_data1['cloudfareDNS'][0]['DNStype']
DNScontent1 = json_data1['cloudfareDNS'][0]['DNScontent']
name1 = json_data1['cloudfareDNS'][0]['name']
proxied1 = json_data1['cloudfareDNS'][0]['proxied']


DNStype2 = json_data1['cloudfareDNS'][1]['DNStype']
DNScontent2 = json_data1['cloudfareDNS'][1]['DNScontent']
name2 = json_data1['cloudfareDNS'][1]['name']
proxied2 = json_data1['cloudfareDNS'][1]['proxied']

#检测API可用性
usable = APIusability(Authorization)
if usable['errors'] == []:
    print('APIKEY授权检测通过')
elif usable['errors'] != []:
    print('APIKEY授权错误,请检查KEY可用性')
    sys.exit(0)

while True:
    print('主程序开始运行')
    #执行IP拔测
    delay, result, date = ping_ip(IP,pingTime)
    with open('results.json', 'a') as f:  # 'a'表示追加模式
        f.write(json.dumps({'date': date, 'delay': int(delay)}))  # 将字典转化为字符串并写入文件
        f.write('\n')  # 换行
    arr = filewrit(int(delay))
    if len(arr)>=pollTime:
        sum_of_elements = 0
        for element in arr:
            # 将每个元素加到总和中
            sum_of_elements += element
            # 计算平均值
        average = sum_of_elements / len(arr)
        # 输出平均值
        meanvalue = average
        print("平均值:", meanvalue)
        os.remove("data.txt")

        with open('file.txt', 'r') as file:
            bool_value = file.read()  # 读取文件内容
            bool_value1 = bool(bool_value)  # 把字符串转换回布尔值

        if meanvalue>=overtime:
            if bool_value1 != True:
                print("延迟超过设定值，执行变更备用IP请求")
                with open('file.txt', 'w') as file:
                    file.write(str(True))  # 把布尔值转换为字符串然后写入文件
                    file.close()
                Update_DNS(DNStype2, DNScontent2, name2, proxied2)
                print("变更备用IP请求完毕")
        else:
            if bool_value1:
                print("主IP恢复正常，执行变更主IP请求")
                with open('file.txt', 'w') as file:
                    pass
                # 变更DNS记录
                Update_DNS(DNStype1, DNScontent1, name1, proxied1)
                print("变更主IP请求完毕")
            else:
                print('主IP延迟无变化')
    time.sleep(Time)
