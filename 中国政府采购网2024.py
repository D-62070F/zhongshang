import json
import random
import re
import threading
import time
import warnings
import pymysql
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from lxml import etree
from w3lib import html
import sys

warnings.filterwarnings('ignore')
sys.setrecursionlimit(3000)
proxy_list = []

global proxys, start, sqllist, errourl_list


def get_current_proxy():
    if proxy_list:
        return proxy_list[-1]
    else:
        return None

def save_to_file(filename, content):
    with open(filename, 'a+') as f:
        f.write(content + '\n')


def daili():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url = 'http://api.tianqiip.com/getip?secret=w1p0qoi2zkhq7aj1&num=1&type=json&port=1&time=3&sign=15535e2d5eb8158fbaab951e677ac233'
    resp = requests.get(url)
    Json = json.loads(resp.text)
    print(Json)
    ipproxy = str(Json['data'][0]['ip']) + ':' + str(Json['data'][0]['port'])
    proxy = {
        'http': f'http://{ipproxy}',
        'https': f'https://{ipproxy}'  # 可以找找国内的一些免费ip
    }
    save_to_file('proxy.txt', f"{current_time}: {proxy}")

    try:
        time.sleep(1)
        result = requests.get("http://httpbin.org/ip", proxies=proxy, timeout=10)
        print(result.text)
        return proxy
    except Exception as e:
        print(f"请求失败，代理IP无效！{e}")
        save_to_file('error_log.txt', f"{current_time}: {e}")
        return None


def func(listTemp, n):
    aaa = []
    for i in range(0, len(listTemp), n):
        aaa.append(listTemp[i:i + n])
    return aaa

def main():
    schedule_thread = threading.Thread(target=change_proxy)
    schedule_thread.start()

def run():
    global proxys, start, sqllist, errourl_list
    main()
    time.sleep(5)
    db = pymysql.connect(host='192.168.1.247',  # MySQL所在电脑的 ip
                         port=3306,  # 端口
                         user='Enterprise',  # 用户名
                         password='123456',  # 密码
                         db='purchase',  # 数据库名
                         autocommit=True)
    url = 'https://search.ccgp.gov.cn/bxsearch'
    for num in range(1, 2915):
        print(f'爬取第 {num} 页')
        param = {
            "searchtype": "1",
            "page_index": f"{num}",
            "bidSort": "2",
            "buyerName": "",
            "projectId": "",
            "pinMu": "0",
            "bidType": "",
            "dbselect": "bidx",
            "kw": "",
            "start_time": "2024:02:01",
            "end_time": "2024:02:29",
            "timeType": "6",
            "displayZone": "",
            "zoneId": "",
            "pppStatus": "0",
            "agentName": ""
        }
        if num == 1:
            query_string = f'https://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index={num + 1}&bidSort=2&buyerName=&projectId=&pinMu=0&bidType=&dbselect=bidx&kw=&start_time=2024%3A02%3A01&end_time=2024%3A02%3A29&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName='
        else:
            query_string = f'https://search.ccgp.gov.cn/bxsearch?searchtype=1&page_index={num - 1}&bidSort=2&buyerName=&projectId=&pinMu=0&bidType=&dbselect=bidx&kw=&start_time=2024%3A02%3A01&end_time=2024%3A02%3A29&timeType=6&displayZone=&zoneId=&pppStatus=0&agentName='
        new_url = query_string
        print('来源：', new_url)
        header = {
            "Host": "search.ccgp.gov.cn",
            'Referer': new_url,
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        while True:
            responses = demand(url, param, header, num)
            if responses:
                break
            else:
                time.sleep(random.uniform(1, 15))
        responses.encoding = 'UTF-8'
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

        if errourl_list:
            try:
                db.ping(reconnect=True)
                cursor = db.cursor()
                sql = 'INSERT INTO not_collected (url, Creation_time) VALUES (%s, %s)'
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
        time.sleep(random.uniform(1, 7))
        print('*' * 68)


def demand(url, param, header, num):
    global proxys
    proxys = get_current_proxy()
    try:
        response = requests.get(url, params=param, headers=header, timeout=10, proxies=proxys,
                                verify=False)  # , impersonate="chrome101"
        print('正在爬取得网址：', response.url)
        print(response.status_code)
        if response.status_code == 200:
            return response
        else:
            return False
    except Exception as e:
        print(f'爬取第{num}页报错', e)
        time.sleep(random.uniform(0, 5))
        return False


def demand2(url):
    global proxys
    try:
        if url[0:4] != 'http':
            _url = 'http:' + url
        else:
            _url = url
        header = {
            "Host": "www.ccgp.gov.cn",
            'Referer': 'http://search.ccgp.gov.cn/',
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        response = requests.get(_url, headers=header, timeout=10, proxies=proxys,
                                verify=False)  # , impersonate="chrome101"
        print(response.status_code)
        print(response.url)
        if response.status_code == 200:
            return response
        else:
            return False
    except Exception as e:
        print('爬取报错', e)
        time.sleep(random.uniform(0, 5))
        return False


def analysis(url_hrefs):
    global proxys, start, sqllist, errourl_list
    for url_href in url_hrefs:
        # while True:
        res = demand2(url_href)
        if res:
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
        else:
            today = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            errosql = [url_href, today]
            errourl_list.append(errosql)
            # break



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


def change_proxy():
    while True:
        proxy = daili()
        if proxy:
            proxy_list.append(proxy)
            print(f"成功设置新的代理 IP: {proxy}")
            time.sleep(120)  # 每两分钟更换一次代理IP
        else:
            print("获取代理 IP 失败，等待重试")


if __name__ == '__main__':
    run()
