import json
import os
import random
import re
import sys
from w3lib import html
from bs4 import BeautifulSoup
import threading
import time
import warnings
import pymysql
import requests
from datetime import datetime
from lxml import etree

global start, sqllist, errourl_list
warnings.filterwarnings('ignore')
sys.setrecursionlimit(3000)
proxy_list = []

def func(listTemp, n):
    aaa = []
    for i in range(0, len(listTemp), n):
        aaa.append(listTemp[i:i + n])
    return aaa


def change_proxy():
    while True:
        proxy = get_proxy()
        if proxy:
            proxy_list.append(proxy)
            print(f"成功设置新的代理 IP: {proxy}")
            time.sleep(60)  # 每两分钟更换一次代理IP
        else:
            print("获取代理 IP 失败，等待重试")

def save_to_file(filename, content):
    with open(filename, 'a+') as f:
        f.write(content + '\n')

def get_proxy():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        proxy_pool_url = 'http://api.tianqiip.com/getip?secret=w1p0qoi2zkhq7aj1&num=1&type=json&port=1&time=3&sign=15535e2d5eb8158fbaab951e677ac233'
        response = requests.get(proxy_pool_url)
        if response.status_code == 200:
            Json = json.loads(response.text)
            ipproxy = str(Json['data'][0]['ip']) + ':' + str(Json['data'][0]['port'])
            proxy = {
                'http': f'http://{ipproxy}',
                'https': f'https://{ipproxy}'  # 可以找找国内的一些免费ip
            }
            save_to_file('proxy.txt', f"{current_time}: {proxy}")
            return proxy
        else:
            print("无法获取代理 IP")
            save_to_file('error_log.txt', f"{current_time}: 获取不了IP")
            return None
    except Exception as e:
        print("获取代理 IP 出错:", e)
        save_to_file('error_log.txt', f"{current_time}: {e}")
        return None

def get_current_proxy():
    if proxy_list:
        return proxy_list[-1]
    else:
        return None


def demand(url, param, header):
    while True:
        proxy = get_current_proxy()
        if not proxy:
            print("没有可用的代理 IP，等待获取新的代理 IP...")
            time.sleep(10)
            continue
        try:
            response = requests.get(url, params=param, headers=header, timeout=10, proxies=proxy, verify=False)
            print(proxy)
            print('正在爬取的网址：', response.url)
            print(response.status_code)
            if response.status_code == 200:
                return response
            else:
                time.sleep(3)
                return False
        except Exception as e:
            print('爬取报错', e)
            time.sleep(random.uniform(0, 3))
            return None

def demand2(url):
    while True:
        proxy = get_current_proxy()
        if not proxy:
            print("没有可用的代理 IP，等待获取新的代理 IP...")
            time.sleep(10)
            continue
        try:
            if url[0:4] != 'http':
                _url = 'http:' + url
            else:
                _url = url
            header = {
                'Host': 'www.ccgp.gov.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }
            response = requests.get(_url, headers=header, timeout=10, proxies=proxy, verify=False)
            print(proxy)
            print(response.status_code)
            print(response.url)
            if response.status_code == 200:
                return response
            else:
                time.sleep(3)
                return None
        except Exception as e:
            print('爬取报错', e)
            time.sleep(random.uniform(0, 5))
            return None

def analysis(url_hrefs):
    global start, sqllist, errourl_list
    for url_href in url_hrefs:
        print(url_href)
        while True:
            res = demand2(url_href)
            if res:
                break
            else:
                errosql = [url_href]
                errourl_list.append(errosql)
                # time.sleep(random.uniform(1, 15))
        res.encoding = 'UTF-8'
        soup = BeautifulSoup(res.text, 'lxml')
        try:
            title = soup.select('h2')[0].text
        except:
            title = soup.select('h2.tc')[0].text
        print('公告标题：', title)
        times = soup.select('#pubTime')[0].text.replace('年', '-').replace('月', '-').replace('日', '')
        print('时间：', times)
        try:
            content = soup.select('.vT_detail_content')[0]
        except:
            content = soup.select('.vF_detail_content')[0]
        try:
            content = wash_data(content)
        except:
            content = str(content)
        if '日</span> </p>' in content:
            new_content = content.rsplit('日</span> </p>', 1)[0] + '日</span> </p>'
        else:
            new_content = content.strip()
        try:
            precis = soup.select('.table table')[0]
            precis = wash_data(precis)
        except:
            precis = None
            print('没有公告摘要')
        try:
            href = soup.select('.table')[0].text
            cgdw = re.findall('联系人及联系方式：.*?采购单位(.*?)采购单位地址', str(href))[0]
            print('采购单位:', cgdw)
            cgdwdz = re.findall('采购单位地址(.*?)采购单位联系方式', str(href))[0]
            print('采购单位地址:', cgdwdz)
            lxfs = re.findall('采购单位联系方式(.*?)代理机构名称', str(href))[0]
            print('采购单位联系方式:', lxfs)
        except:
            cgdw = None
            cgdwdz = None
            lxfs = None
            print('联系方式读取错误')
        res.close()

        today = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print('生成sql语句')
        print()
        param = [url_href, title, times, '地方公告', new_content, precis, today, cgdw, cgdwdz, lxfs]
        sqllist.append(param)

    # return sqllist

def wash_data(content):
    for tag in content.find_all():
        if tag.name == 'a':
            new_attrs = {}
            if 'href' in tag.attrs:
                new_attrs['href'] = tag.attrs['href']
            tag.attrs = new_attrs
        elif tag.name == 'td':
            new_attrs = {}
            if 'colspan' in tag.attrs:
                new_attrs['colspan'] = tag.attrs['colspan']
            if 'rowspan' in tag.attrs:
                new_attrs['rowspan'] = tag.attrs['rowspan']
            tag.attrs = new_attrs
        elif tag.name == 'img':
            new_attrs = {}
            if 'src' in tag.attrs:
                new_attrs['src'] = tag.attrs['src']
            tag.attrs = new_attrs
        else:
            tag.attrs = {}
    re_comment = re.compile('<!--[^>]*-->')
    re_comment2 = re.compile(r'<!-[\s\S]*?-->')
    re_href = re.compile(r'href="javascript:void\(0\);"')
    re_href2 = re.compile(r'href="#"')
    re_span = re.compile(r'<span.*?>')
    tb_re = re.compile(r'<table.*?>')

    content = html.remove_tags(str(content), (
        "div", "font", "iframe", "video", "input", "meta", "object", "form",
        "o:p", "link", "script", "textarea", "colgroup", 'col', "o:lock", "u"),
                               encoding="utf-8", )
    content = re_comment.sub('', str(content))
    content = re_comment2.sub('', str(content))
    content = re_href.sub('', str(content))
    content = re_href2.sub('', str(content))
    content = tb_re.sub('<table>', str(content))
    content = re_span.sub('<span>', str(content))
    content = re.sub('\n', '', str(content))
    return content

def run():
    global start, sqllist, errourl_list
    while True:
        db = pymysql.connect(host='192.168.1.247',  # MySQL所在电脑的 ip
                             port=3306,  # 端口
                             user='Enterprise',  # 用户名
                             password='123456',  # 密码
                             db='purchase',  # 数据库名
                             autocommit=True)
        url = 'https://search.ccgp.gov.cn/bxsearch'
        for num in range(1, 2):#906
            print(f'爬取第 {num} 页')
            param = {
                "searchtype": "1",
                "page_index": f"{num}",
                "bidSort": "1",
                "buyerName": "",
                "projectId": "",
                "pinMu": "0",
                "bidType": "",
                "dbselect": "bidx",
                "kw": "",
                "start_time": "2024:01:01",
                "end_time": "2024:04:10",
                "timeType": "6",
                "displayZone": "",
                "zoneId": "",
                "pppStatus": "0",
                "agentName": ""
            }
            if num == 1:
                query_string = f'https://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index={num + 1}&bidSort=2&buyerName=&projectId=&pinMu=0&bidType=&dbselect=bidx&kw=&start_time=2023%3A01%3A01&end_time=2023%3A12%3A31&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName='
            else:
                query_string = f'https://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index={num - 1}&bidSort=2&buyerName=&projectId=&pinMu=0&bidType=&dbselect=bidx&kw=&start_time=2023%3A01%3A01&end_time=2023%3A12%3A31&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName='
            new_url = query_string
            print('来源：', new_url)
            header = {
                "Host": "search.ccgp.gov.cn",
                'Referer': new_url,
                "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }
            while True:
                responses = demand(url, param, header)
                if responses:
                    break
                else:
                    time.sleep(random.uniform(3, 9))
            responses.encoding = 'UTF-8'
            print(responses.text)
            Html = etree.HTML(responses.text)
            uls = Html.xpath('/html/body/div[5]/div[2]/div/div/div[1]/ul/li/a')
            CJlist = []
            for a in uls:
                url_href = a.xpath('./@href')[0]
                CJlist.append(url_href)
            NCJlist = sorted(set(CJlist), key=CJlist.index)
            temp = func(NCJlist, 10)
            thread_list = []
            sqllist = []
            errourl_list = []
            for i in temp:
                t = threading.Thread(target=analysis, args=(i,))
                t.setDaemon(True)
                thread_list.append(t)

            for t in thread_list:
                t.start()
                time.sleep(random.uniform(3, 5))

            for t in thread_list:
                t.join()

            try:
                db.ping(reconnect=True)
                cursor = db.cursor()
                sql = 'INSERT INTO not_collected (url) VALUES %s'
                cursor.executemany(sql, errourl_list)
                db.commit()
                print('执行sql语句——数据存储成功。')
                cursor.close()
            except Exception as e:
                print('数据存储报错：', e)
                db.rollback()
            try:
                db.ping(reconnect=True)
                cursor = db.cursor()
                sql = 'INSERT INTO record_2024(Announcement_url, Announcement, Announcement_time, category, Announcement_text, Announcement_abstract, Creation_time, buying_unit, Unit_address, contact) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                cursor.executemany(sql, sqllist)
                db.commit()
                print('执行sql语句——数据存储成功。')
                cursor.close()
            except Exception as e:
                print(e)
                db.rollback()
            db.close()
            sqllist.clear()
            CJlist.clear()
            errourl_list.clear()
            time.sleep(random.uniform(1, 5))
            print('*' * 68)

if __name__ == '__main__':
    schedule_thread = threading.Thread(target=change_proxy)
    schedule_thread.start()

    run()
