"""
#!/usr/bin/env python
# -*- coding:utf-8 -*-
@File : 旧版政府网站采集.py
@Author : Zeng
@Time : 2023/8/23 14:48
"""
import re
import threading
import time
import traceback
import requests
import schedule as schedule
from bs4 import BeautifulSoup
import socket
import urllib3
import pymysql
import datetime
from w3lib import html
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from fake_useragent import UserAgent

global url_list, fwzh, origin, province, city, county, counurlty, new_urllist, _num

socket.setdefaulttimeout(20)  # 设置HTTP或Socket超时，来防止爬虫爬取某个页面时间过长
urllib3.disable_warnings()  # 证书认证及警告的禁用
province_list = ["北京", "天津", "河北", "山西", "内蒙古", "辽宁", "吉林", "黑龙江",
                 "上海", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北",
                 "湖南", "广东", "广西", "海南", "重庆", "四川", "贵州", "云南", "西藏",
                 "陕西", "甘肃", "青海", "宁夏", "新疆", "香港", "澳门", "台湾", "新疆"]
ua = UserAgent()


def func(listTemp, n):
    aaa = []
    for i in range(0, len(listTemp), n):
        aaa.append(listTemp[i:i + n])
    return aaa


def get_data():
    db_host = "askci-db.rwlb.rds.aliyuncs.com"
    db_user = "datauser_collect"
    db_pwd = "uPTZ5y@xNy8PhEeR"
    db_port = 3306
    db_name = "collectdata"
    conn = pymysql.connect(host=db_host, user=db_user, password=db_pwd, port=db_port, db=db_name, autocommit=True)
    cur = conn.cursor()
    # selsql = 'SELECT Regionid,PolicySourceUrl,LinkExpression,GetIdExpression,ContentExpression,AnnexExpression,sort,CollectDate,PageUpDate,titleExpression,timeExpression FROM PolicySource  WHERE DATE_FORMAT(CollectDate,"%Y-%m-%d") < CURDATE() or (CollectDate is null  and parameter is null)'
    selsql = 'SELECT Regionid,PolicySourceUrl,LinkExpression,GetIdExpression,ContentExpression,AnnexExpression,PageUpDate,titleExpression,timeExpression FROM PolicySource WHERE DATE_FORMAT(CollectDate,"%Y-%m-%d") < CURDATE() LIMIT 15000'  # WHERE  CollectDate is not null and add_num = 0
    cur.execute(selsql)  # 执行sql语句
    results = cur.fetchall()  # 将查询结果返回成一个元组
    cur.close()  # 关闭游标对象，该游标对象无法再使用
    conn.close()  # 关闭数据库连接
    return results


def Run(record):
    """
    :param record: 查询数据库返回的数据
    判断网页是否有翻页
    输入获取内容的表达式
    """
    global url_list, new_urllist, _num
    url_list = []  # 需要抓取的Url集合
    new_urllist = []  # 数据库没有的Url集合
    _num = []  # 成功插入数据的集合
    for y in record:
        area = y[0]  # 网址所属区域
        url = y[1]  # 需要采集的Url
        href_voice = y[2]  # 获取href的表达式
        ID_Splicing = y[3]
        content_voice = y[4]  # 获取内容的表达式
        annex_voice = y[5]  # 获取附件的表达式
        fy_date = y[6]  # 翻页日期
        title_voice = y[7]  # 获取标题的表达式
        time_voice = y[8]  # 获取时间的表达式
        print('爬取的URL：', url)
        get_Url(url, url_list, href_voice, fy_date)  # GET请求
        ly = get_origin(url)  # 文章来源
        url_list = sorted(list(set(url_list)), key=url_list.index)  # 集合去重
        print('一共有', len(url_list), '个网址需要抓取')
        url_list = joint_http(url_list, ID_Splicing)  # 链接拼接
        if len(url_list) == 0:
            db_host = "askci-db.rwlb.rds.aliyuncs.com"
            db_user = "datauser_collect"
            db_pwd = "uPTZ5y@xNy8PhEeR"
            db_port = 3306
            db_name = "collectdata"
            conn = pymysql.connect(host=db_host, user=db_user, password=db_pwd, port=db_port, db=db_name,
                                   autocommit=True)
            cur = conn.cursor()
            today = str(datetime.datetime.now())[:-3]
            add_sql = "UPDATE PolicySource SET add_num = '%s', CollectDate = '%s' WHERE PolicySourceUrl = '%s'" % (
                0, today, url)
            try:
                cur.execute(add_sql)  # 执行sql语句
            except:
                conn.rollback()  # 发生错误时回滚
            cur.close()
            conn.close()
        sel_url(url_list, new_urllist, fy_date)  # 数据查询是否存在
        if len(new_urllist) >= 20:
            updata_sql(url)
        if new_urllist:
            db_host = "askci-db.rwlb.rds.aliyuncs.com"
            db_user = "datauser_collect"
            db_pwd = "uPTZ5y@xNy8PhEeR"
            db_port = 3306
            db_name = "collectdata"
            conn = pymysql.connect(host=db_host, user=db_user, password=db_pwd, port=db_port, db=db_name,
                                   autocommit=True)
            cur = conn.cursor()
            add_sql = "UPDATE PolicySource SET need_num = '%s' WHERE PolicySourceUrl = '%s'" % (
                len(new_urllist), url)
            try:
                print(f'新增 {len(new_urllist)} 条数据库不存在的数据')
                cur.execute(add_sql)  # 执行sql语句
            except:
                conn.rollback()  # 发生错误时回滚
            cur.close()
            conn.close()
            urlnum = 0
            for i in new_urllist:
                new_url = i
                print(new_url)
                urlnum += 1
                print('在爬取第', urlnum, '个网址')
                get_shuju(new_url, urlnum, content_voice, annex_voice, area, ly, url, title_voice, time_voice)
            upcj_sql(url, url_list)
            N_num = len(_num)
            print(N_num)
            succ_sql(N_num, url)
        else:
            upcj_sql(url, url_list)
            print('-----------------------------没有新的数据需要采集-----------------------------', '\n')
        url_list.clear()
        new_urllist.clear()
        _num.clear()
        print('=' * 77)
        # break


def get_Url(url, url_list, href_voice, fy_date):
    """获取详情连接"""
    try:
        code_url = []
        if 'index.htm' in url and fy_date == 'None' or 'index.htm' in url and fy_date is None:
            errolnum = 0
            for page in range(1, 80):
                if errolnum == 3:
                    break  # 请求翻页三次失败后不再翻页
                if page == 1:
                    on_url = url
                else:
                    on_url = str(url).strip().replace('index.', f'index_{page}.')
                res_code = requests.get(on_url, headers={'User-Agent': ua.chrome}, timeout=20, verify=False).status_code
                if res_code == 200 or res_code == 202:
                    code_url.append(on_url)
                else:
                    errolnum += 1
        else:
            res_code = requests.get(url, headers={'User-Agent': ua.chrome}, timeout=20, verify=False).status_code
            if res_code == 200 or res_code == 202 or res_code == 412 or res_code == 521:
                code_url.append(url)
        for ons_url in code_url:
            res = requests.get(ons_url, headers={'User-Agent': ua.chrome}, timeout=20, verify=False)
            if res.status_code == 202 or res.status_code == 412:
                #   Firefox请求
                options = FirefoxOptions()
                options.add_argument("--headless")
                driver = webdriver.Firefox(options=options)
                driver.set_window_size(1454, 986)
                driver.get(ons_url)
                driver.implicitly_wait(10)
                time.sleep(3)
                html_source = driver.page_source
                soup = BeautifulSoup(html_source, 'lxml')
                driver.quit()
            elif res.status_code == 521:
                print('EDGE')
                options = webdriver.EdgeOptions()
                options.add_argument("--enable-features=NetworkServiceInProcess")
                options.add_argument("headless")
                options.add_argument("--disable-gpu")
                options.add_experimental_option('useAutomationExtension', False)
                options.add_experimental_option('excludeSwitches', ['enable-automation'])
                options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
                options.add_argument('--disable-blink-features=AutomationControlled')
                driver = webdriver.Edge(options=options)
                driver.get(ons_url)
                driver.implicitly_wait(10)
                time.sleep(3)
                html_source = driver.page_source
                soup = BeautifulSoup(html_source, 'lxml')
                driver.quit()
            else:
                res.encoding = 'utf-8'  # 设置编码
                html_source = res.text
                soup = BeautifulSoup(html_source, 'lxml')
            # print(soup)
            if '(.*?)' not in href_voice:
                uls = soup.select(href_voice + ' a')
                # print(uls)
                if not uls:
                    href_voice = href_voice.rsplit(' > div.', 1)[-1]
                    uls = soup.select(f'.{href_voice}' + ' a')
                for ul in uls:
                    href = ul.get('href')
                    if href is not None and href != '':
                        if href[0:4] == 'http':  # 判断链接是否为完整(以http开头）
                            if str(href).split('.')[-1] not in ['docx', 'png', 'doc', 'pdf', 'xlsx', 'xls', 'zip',
                                                                'rtf', 'jpg', 'rar', 'tif', 'ppt', 'mp4', 'asp', 'PDF',
                                                                'wps', 'flv', '7z', 'jpeg', 'pptx', 'et']:  # 判断是否为网页连接
                                url_list.append(str.strip(href))
                            else:
                                print('----------------此链接异常，不是网页url链接----------------')
                        else:
                            get_id = re.findall(r'/[a-zA-Z0-9]\S+|[a-zA-Z0-9]\S+', str(href))  # 不完整以正则表达式获取链接
                            if get_id and get_id is not None and get_id != '':
                                if get_id[0].split('.')[-1] not in ['docx', 'png', 'doc', 'pdf', 'xlsx', 'xls', 'pptx',
                                                                    'zip', 'rtf', 'jpg', 'rar', 'tif', 'ppt', 'mp4',
                                                                    'asp', 'PDF', 'wps', 'flv', '7z', 'jpeg', 'et']:
                                    url_list.append(str.strip(get_id[0]))
                            else:
                                url_list.append(str.strip(href))
            else:
                get_url = re.findall(href_voice, str(soup))
                print(get_url)
                for u in get_url:
                    if u is not None and u != '':
                        n_url = str(u).replace(r'\\', '').replace(r'\/', '/')
                        if str(n_url).split('.')[-1] not in ['docx', 'png', 'doc', 'pdf', 'xlsx', 'xls', 'zip', 'rtf',
                                                             'jpg', 'pptx', 'rar', 'tif', 'ppt', 'mp4', 'asp', 'PDF',
                                                             'wps', 'flv', '7z', 'jpeg', 'et']:
                            url_list.append(str.strip(n_url).rsplit('./', -1)[-1])
    except:
        pass
    return url_list


def joint_http(url_list, ID_Splicing):
    http_list = []
    for _url in url_list:
        if _url[0:4] == 'http':
            http_list.append(_url)
        else:
            if _url != '':
                if ID_Splicing and ID_Splicing != '':
                    if _url[0] == '.' and _url[1] == '/':
                        n_url = ID_Splicing + _url[2:]
                    elif _url[0] == '/' and str(ID_Splicing)[-1] == '/':
                        n_url = ID_Splicing + _url[1:]
                    elif str(ID_Splicing)[-1] != '/' and _url[0] != '/':
                        n_url = ID_Splicing + '/' + _url
                    else:
                        n_url = ID_Splicing + _url
                    http_list.append(n_url)
                else:
                    print('该网站不完整且没有拼接的字段信息')
                    break
    return http_list


def sel_url(url_list, new_urllist, fy_date):
    db_host = "askci-db.rwlb.rds.aliyuncs.com"
    db_user = "datauser_collect"
    db_pwd = "uPTZ5y@xNy8PhEeR"
    db_port = 3306
    db_name = "policydata"
    conn = pymysql.connect(host=db_host, user=db_user, password=db_pwd, port=db_port, db=db_name,
                           autocommit=True)
    cur = conn.cursor()
    if fy_date and fy_date is not None and fy_date != 'None':
        print(fy_date)
        url_list = url_list[:51]
    for Nurl in url_list:
        if Nurl == '#' or Nurl == 'javascript:;':
            pass
        else:
            try:
                Sql = f"select Publish_link from Government_news WHERE Publish_link = '{Nurl}'"
                cur.execute(Sql)  # 执行SQL语句
                LastGetId = cur.fetchall()
                if not LastGetId:
                    print('------------------有一条新的数据需要采集-----------------')
                    new_urllist.append(Nurl)
            except:
                pass
    cur.close()
    conn.close()


def updata_sql(url):
    today = str(datetime.datetime.now())[:-3]
    upsql = "UPDATE PolicySource SET PageUpDate = '%s' WHERE PolicySourceUrl = '%s'" % (today, url)
    db_host = "askci-db.rwlb.rds.aliyuncs.com"
    db_user = "datauser_collect"
    db_pwd = "uPTZ5y@xNy8PhEeR"
    db_port = 3306
    db_name = "collectdata"
    conn = pymysql.connect(host=db_host, user=db_user, password=db_pwd, port=db_port, db=db_name,
                           autocommit=True)
    cur = conn.cursor()
    try:
        cur.execute(upsql)  # 执行sql语句
    except:
        conn.rollback()  # 发生错误时回滚
    cur.close()
    conn.close()


def succ_sql(N_num, url):
    db_host = "askci-db.rwlb.rds.aliyuncs.com"
    db_user = "datauser_collect"
    db_pwd = "uPTZ5y@xNy8PhEeR"
    db_port = 3306
    db_name = "collectdata"
    conn = pymysql.connect(host=db_host, user=db_user, password=db_pwd, port=db_port, db=db_name,
                           autocommit=True)
    cur = conn.cursor()
    _upsql = "UPDATE PolicySource SET success_num = '%s' WHERE PolicySourceUrl = '%s'" % (N_num, url)
    print(_upsql)
    try:
        cur.execute(_upsql)  # 执行sql语句
    except:
        conn.rollback()  # 发生错误时回滚
    cur.close()
    conn.close()


def upcj_sql(url, url_list):
    list_num = len(url_list)
    print('==============更新爬取时间==============')
    today = str(datetime.datetime.now())[:-3]
    if list_num != 0:
        upsql = "UPDATE PolicySource SET add_num = '%s', CollectDate = '%s' WHERE PolicySourceUrl = '%s'" % (
            list_num, today, url)
    else:
        upsql = "UPDATE PolicySource SET add_num = '%s' WHERE PolicySourceUrl = '%s'" % (
            0, url)
    db_host = "askci-db.rwlb.rds.aliyuncs.com"
    db_user = "datauser_collect"
    db_pwd = "uPTZ5y@xNy8PhEeR"
    db_port = 3306
    db_name = "collectdata"
    conn = pymysql.connect(host=db_host, user=db_user, password=db_pwd, port=db_port, db=db_name,
                           autocommit=True)
    cur = conn.cursor()
    try:
        cur.execute(upsql)  # 执行sql语句
    except:
        conn.rollback()  # 发生错误时回滚
    cur.close()
    conn.close()


def get_origin(url):
    """获取文章来源"""
    global origin
    # try:
    try:
        res = requests.get(url, headers={'User-Agent': ua.chrome}, timeout=20, verify=False)
        if res.status_code == 202 or res.status_code == 412:
            #   Firefox请求
            options = FirefoxOptions()
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
            driver.set_window_size(1454, 986)
            driver.get(url)
            driver.implicitly_wait(10)
            time.sleep(3)
            html_source = driver.page_source
            soup = BeautifulSoup(html_source, 'lxml')
            driver.quit()
            try:
                origin = re.findall('<meta content="(.*?)" name="SiteName"/>', str(soup))[0]
                if '_' in origin:
                    origin = re.findall('<meta content="(.*?)_.*?" name="SiteName"/>', str(soup))[0]
                if ',' in origin:
                    origin = re.findall('<meta content=".*?,(.*?)" name="SiteName"/>', str(soup))[0]
            except:
                origin = re.findall('<title>.*?_.*?_(.*?)</title>', str(soup))[0]
        elif int(res.status_code) == 200:  # 判断请求状态码
            charsets = 'UTF-8'
            res.encoding = charsets
            # res.encoding = 'utf-8'  # 设置编码
            res.close()
            soup = BeautifulSoup(res.text, 'lxml')
            try:
                origin = re.findall('<meta content="(.*?)" name="SiteName"/>', str(soup))[0]
                if '_' in origin:
                    origin = re.findall('<meta content="(.*?)_.*?" name="SiteName"/>', str(soup))[0]
                if ',' in origin:
                    origin = re.findall('<meta content=".*?,(.*?)" name="SiteName"/>', str(soup))[0]
            except:
                origin = re.findall('<title>.*?_.*?_(.*?)</title>', str(soup))[0]
        else:
            origin = '-'
            pass
        if '�' in origin:
            res.encoding = 'GB2312'
            soup = BeautifulSoup(res.text, 'lxml')
            try:
                origin = re.findall('<meta content="(.*?)" name="SiteName"/>', str(soup))[0]
                if '_' in origin:
                    origin = re.findall('<meta content="(.*?)_.*?" name="SiteName"/>', str(soup))[0]
                if ',' in origin:
                    origin = re.findall('<meta content=".*?,(.*?)" name="SiteName"/>', str(soup))[0]
            except:
                origin = re.findall('<title>.*?_.*?_(.*?)</title>', str(soup))[0]
    except:
        origin = '-'
    if '"' in origin:
        origin = str(origin).split('"', -1)[-1]
    print('来源：', origin)
    return origin


def get_shuju(new_url, urlnum, content_voice, annex_voice, area, ly, url, title_voice, time_voice):
    """
    :param annex_voice: 获取附件表达式
    :param url: 需要采集的网址
    :param ly: 网址来源
    :param area: 所属区域
    :param UA: 请求头
    :param new_url: 详情页链接
    :param urlnum: 变量记录存储数目
    :param title_voice: 获取标题表达式
    :param time_voice: 获取时间表达式
    :param content_voice: 获取内容表达式
    获取时间、标题、内容；保存图片附件以及数据保存到数据库
    """
    try:
        print('链接： ', new_url, '\n')
        header = {'User-Agent': ua.chrome}
        response = requests.get(new_url, headers=header, timeout=20, verify=False)
        if response.status_code == 200:
            charsets = 'UTF-8'
            web_capture(title_voice, time_voice, content_voice, new_url, annex_voice, urlnum, area, ly,
                        url, response, charsets)
        elif response.status_code == 202 or response.status_code == 412:
            #   Firefox请求
            options = FirefoxOptions()
            options.add_argument("--headless")
            driver = webdriver.Firefox(options=options)
            driver.set_window_size(1454, 986)
            driver.get(new_url)
            driver.implicitly_wait(7)
            time.sleep(3)
            html_source = driver.page_source
            driver.quit()
            web_capture2(html_source, title_voice, time_voice, content_voice, new_url, annex_voice, urlnum, area, ly,
                         url)
        else:
            print(f'请求网址状态异常：{response.url}')
            pass
    except:
        print('该网址抓取报错：', new_url)
        print('爬取报错：', traceback.format_exc())
        pass
    print('*' * 88 + '\n')


def _data(soup, title, time_voice, content_voice, new_url, annex_voice, urlnum, area, ly, url):
    global _num
    source = get_LY(soup, title)  # 获取发布机构
    docnum = get_Document(soup)  # 获取发文字号
    Time = get_SJ(soup, time_voice)  # 获取时间
    content = get_NR(soup, content_voice)  # 获取内容
    if content == 0:
        print('爬取报错不存储数据')
        pass
    else:
        get_TP(soup, content_voice, new_url, annex_voice)  # 保存图片、附件
        Store_data(new_url, title, source, docnum, Time, content, urlnum, area, ly, url)  # 存储数据
        _num.append(new_url)


def web_capture(title_voice, time_voice, content_voice, new_url, annex_voice, urlnum, area, ly, url, response,
                charsets):
    global _num
    response.encoding = charsets
    html_source = response.text
    soup = BeautifulSoup(html_source, 'lxml')
    title = get_BT(soup, title_voice)  # 获取标题
    # 乱码进入这里重新转变编码重新获取存储
    if '�' in title:
        response.encoding = 'GB2312'
        html_source = response.text
        soup = BeautifulSoup(html_source, 'lxml')
        title = get_BT(soup, title_voice)  # 获取标题
        if '�' in title:
            response.encoding = 'GBK'
            html_source = response.text
            soup = BeautifulSoup(html_source, 'lxml')
            title = get_BT(soup, title_voice)  # 获取标题
            _data(soup, title, time_voice, content_voice, new_url, annex_voice, urlnum, area, ly, url)
        else:
            _data(soup, title, time_voice, content_voice, new_url, annex_voice, urlnum, area, ly, url)
    # 没乱码继续获取内容存储
    else:
        _data(soup, title, time_voice, content_voice, new_url, annex_voice, urlnum, area, ly, url)


def web_capture2(html_source, title_voice, time_voice, content_voice, new_url, annex_voice, urlnum, area, ly, url, ):
    soup = BeautifulSoup(html_source, 'lxml')
    title = get_BT(soup, title_voice)  # 获取标题
    soup = BeautifulSoup(html_source, 'lxml')
    source = get_LY(soup, title)  # 获取发布机构
    docnum = get_Document(soup)  # 获取发文字号
    Time = get_SJ(soup, time_voice)  # 获取时间
    content = get_NR(soup, content_voice)  # 获取内容
    if content == 0:
        print('爬取报错不存储数据')
        pass
    else:
        get_TP(soup, content_voice, new_url, annex_voice)  # 保存图片、附件
        Store_data(new_url, title, source, docnum, Time, content, urlnum, area, ly, url)  # 存储数据
        _num.append(new_url)


def get_BT(soup, title_voice):
    """获取标题"""
    if title_voice and title_voice != '':
        try:
            # Title = soup.xpath(time_voice)[0].strip()
            Title = soup.select(title_voice)[0].text.strip()
        except:
            Title = re.findall(title_voice, str(soup))[0].strip()
    else:
        try:
            Title = re.findall(r'meta content="(.*?)" name=.*?ArticleTitle.*?>', str(soup))[0].strip()
        except:
            try:
                Title = re.findall(r'meta content="(.*?)" name="[k|K]eywords"/>', str(soup))[0].strip()
            except:
                tag = 'title'
                Title = re.findall(r'(?<=<' + tag + '>).*?(?=</' + tag + '>)', str(soup))[0].strip()
    if not Title:
        tag = 'title'
        Title = re.findall(r'(?<=<' + tag + '>).*?(?=</' + tag + '>)', str(soup))[0].strip()
        # Title = re.findall(r'<title>(.*?)</title>', str(soup), re.S)[0].strip()
    if Title == '':
        Title = re.findall(r'<h1>(.*?)</h1>', str(soup), re.S)[0].strip()
    Title = Title.replace('&lt;br&gt;', '').replace('■', '').replace('\n', '').replace(' ', '').replace('&lt;br/&gt;', '').replace('&lt;', '')
    if '<metacontent="' in Title:
        Title = Title.rsplit('<metacontent="', -1)[-1]
    print('标题： ', Title)
    return Title


def get_LY(soup, title):
    """获取发布机构"""
    # print(soup)
    try:
        try:
            Source = re.findall('<meta content="(.*?)" name="[C|c]ontentSource"/>', str(soup))[0].strip()
            if Source == '本网' or Source == '通知公告' or Source == '-' or Source == '' or '" name' in Source:
                Source = re.findall('<meta content="(.*?)" name="SiteName"/>', str(soup))[0].strip()
        except:
            try:
                Source = re.findall('发文机关[：|:](.*?)成文', str(soup.text), re.S)[0].strip()
            except:
                Source = '-'
        if ' ' in Source:
            Source = Source.rsplit(' ', 1)[0].replace('《', '')
        if '" name' in Source:
            Source = Source.rsplit('" name', 1)[0]
        if Source == title:
            Source = '-'
        if '年' in Source:
            Source = '-'
        report = str('发布机构： ' + Source)
        print(report)
        return Source
    except Exception as e:
        YC = '发布机构' + str(e)
        print(YC)


def get_Document(soup):
    """获取发文字号"""
    global fwzh
    no_list = ['大中小', '小中大', '[大]', '[中]', '[小]', '【大  中  小】', 'ICP']
    try:
        try:
            qw = str(soup.text).strip().replace(' ', '').replace('　', '').replace(' ', '').replace('\t', '')
            wenhao = re.findall('[文|字|编]号(.*?)号', str(qw), re.S)
            if not wenhao:
                wenhao = re.findall('[文|字|编]号[：|:](.*?)号', str(qw), re.S)
            if wenhao:
                fwzh = str(wenhao[0] + '号').replace('\n', '').replace('\r', '')
            else:
                fwzh = '-'
        except:
            fwzh = '-'
        if len(fwzh) > 22:
            fwzh = '-'
        for nw in no_list:
            if nw in fwzh:
                fwzh = '-'
                break
        report = str('发文字号： ' + fwzh)
        print(report)
        if fwzh[0] == ':' or fwzh[0] == '：' or fwzh[0] == ']':
            return fwzh[1:].strip()
        else:
            return fwzh.strip()
    except Exception as e:
        YC = '发文字号' + str(e)
        print(YC)


def get_SJ(soup, time_voice):
    """获取时间"""
    try:
        FBtime = soup.select(time_voice)[0].text.strip()
        # FBtime = soup.xpath(time_voice)[0]
        Time_show = str(FBtime).replace('年', '-').replace('月', '-').replace('日', '-') \
            .replace('/', '-').replace('.', '-').replace('\n', '').replace(' ', '')
        Time_RE = re.findall("(?P<YYYY>\\d{4})-(?P<MM>\\d{1,2})-(?P<dd>\\d{1,2})", str(Time_show))[0]
        Time_RE1 = "-".join(Time_RE)
    except:
        Time_RE = re.findall("(?P<YYYY>\\d{4})[-|/](?P<MM>\\d{1,2})[-|/](?P<dd>\\d{1,2})", str(soup))[0]
        Time_RE1 = "-".join(Time_RE)
    print('发布时间： ', Time_RE1)
    return Time_RE1


def get_NR(soup, content_voice):
    """获取内容"""
    try:
        Now_time = str(datetime.datetime.now())[:10] + '/'
        imgs = soup.find_all("img")
        for img in imgs:
            if img.get('src'):
                img["src"] = '/upload/PictureUpload/' + Now_time + img["src"].split("/")[-1]
        try:
            FB_content = soup.select(content_voice)[0]
        except:
            content_voice = content_voice.rsplit(' > div.', 1)[-1]
            FB_content = soup.select(f'.{content_voice}')[0]
        [s.extract() for s in FB_content('script')]
        [s.extract() for s in FB_content('style')]
        report = str(FB_content.text[:168].strip())
        print('文章内容：', report)
        clean_FB_content = wash(FB_content)
        return clean_FB_content
    except Exception as e:
        print('获取内容报错：' + str(e))
        return 0


def wash(content):
    WJ_hz = ['zip', 'txt', 'doc', 'xls', 'ppt', 'docx', 'xlsx', 'pptx', 'pdf', 'tiff', 'swf',
             'rar', 'jpg', 'tif', 'png', 'ofd', 'PDF', 'DOC', 'XLS', 'wps', 'et']
    for a in content.findAll('a'):
        try:
            if a.text.split('.')[-1] in WJ_hz or a['href'].split('.')[-1] in WJ_hz:
                del a['href']
        except:
            pass
    new_img = []
    re_imga = re.findall('data-needdownload="(.*?)"', str(content))
    for i in re_imga:
        new_i = 'data-needdownload="' + i + '"'
        new_img.append(new_i)
    re_imga2 = re.findall('data-uploadpic="(.*?)"', str(content))
    for i in re_imga2:
        new_i = 'data-uploadpic="' + i + '"'
        new_img.append(new_i)
    re_imga3 = re.findall('uploadpic="(.*?)"', str(content))
    for i in re_imga3:
        new_i = 'uploadpic="' + i + '"'
        new_img.append(new_i)
    re_imga4 = re.findall('needdownload="(.*?)"', str(content))
    for i in re_imga4:
        new_i = 'needdownload="' + i + '"'
        new_img.append(new_i)
    re_imga5 = re.findall('title="(.*?)"', str(content))
    for i in re_imga5:
        new_i = 'title="' + i + '"'
        new_img.append(new_i)
    re_imga6 = re.findall('realt="(.*?)"', str(content))
    for i in re_imga6:
        new_i = 'realt="' + i + '"'
        new_img.append(new_i)
    re_imga7 = re.findall('style="(.*?)"', str(content))
    for i in re_imga7:
        new_i = 'style="' + i + '"'
        new_img.append(new_i)
    re_imga8 = re.findall('picname="(.*?)"', str(content))
    for i in re_imga8:
        new_i = 'picname="' + i + '"'
        new_img.append(new_i)
    re_imga9 = re.findall('oldsrc="(.*?)"', str(content))
    for i in re_imga9:
        new_i = 'oldsrc="' + i + '"'
        new_img.append(new_i)
    re_imga10 = re.findall('_width="(.*?)"', str(content))
    for i in re_imga10:
        new_i = '_width="' + i + '"'
        new_img.append(new_i)
    re_imga11 = re.findall('height="(.*?)"', str(content))
    for i in re_imga11:
        new_i = 'height="' + i + '"'
        new_img.append(new_i)
    re_imga12 = re.findall('appendix="(.*?)"', str(content))
    for i in re_imga12:
        new_i = 'appendix="' + i + '"'
        new_img.append(new_i)
    re_imga13 = re.findall('data-appendix="(.*?)"', str(content))
    for i in re_imga13:
        new_i = 'data-appendix="' + i + '"'
        new_img.append(new_i)
    re_imga14 = re.findall('data-otheroperation="(.*?)"', str(content))
    for i in re_imga14:
        new_i = 'data-otheroperation="' + i + '"'
        new_img.append(new_i)
    re_imga15 = re.findall('otheroperation="(.*?)"', str(content))
    for i in re_imga15:
        new_i = 'otheroperation="' + i + '"'
        new_img.append(new_i)
    re_imga16 = re.findall('target="(.*?)"', str(content))
    for i in re_imga16:
        new_i = 'target="' + i + '"'
        new_img.append(new_i)
    re_imga17 = re.findall('border="(.*?)"', str(content))
    for i in re_imga17:
        new_i = 'border="' + i + '"'
        new_img.append(new_i)
    re_imga18 = re.findall('old="(.*?)"', str(content))
    for i in re_imga18:
        new_i = 'old="' + i + '"'
        new_img.append(new_i)
    re_imga19 = re.findall('attachment-id="(.*?)"', str(content))
    for i in re_imga19:
        new_i = 'attachment-id="' + i + '"'
        new_img.append(new_i)
    re_imga20 = re.findall('name="(.*?)"', str(content))
    for i in re_imga20:
        new_i = 'name="' + i + '"'
        new_img.append(new_i)
    re_imga21 = re.findall('alt="(.*?)"', str(content))
    for i in re_imga21:
        new_i = 'alt="' + i + '"'
        new_img.append(new_i)
    re_imga22 = re.findall('vspace="(.*?)"', str(content))
    for i in re_imga22:
        new_i = 'vspace="' + i + '"'
        new_img.append(new_i)
    re_imga23 = re.findall('img-id="(.*?)"', str(content))
    for i in re_imga23:
        new_i = 'img-id="' + i + '"'
        new_img.append(new_i)
    re_imga24 = re.findall('download="(.*?)"', str(content))
    for i in re_imga24:
        new_i = 'download="' + i + '"'
        new_img.append(new_i)
    re_imga25 = re.findall('class="(.*?)"', str(content))
    for i in re_imga25:
        new_i = 'class="' + i + '"'
        new_img.append(new_i)
    re_imga26 = re.findall("style='(.*?)'", str(content))
    for i in re_imga26:
        new_i = "style='" + i + "'"
        new_img.append(new_i)
    re_imga27 = re.findall('clear="(.*?)"', str(content))
    for i in re_imga27:
        new_i = 'clear="' + i + '"'
        new_img.append(new_i)
    re_imga28 = re.findall('origin="(.*?)"', str(content))
    for i in re_imga28:
        new_i = 'origin="' + i + '"'
        new_img.append(new_i)
    re_imga29 = re.findall('onclick="(.*?)"', str(content))
    for i in re_imga29:
        new_i = 'onclick="' + i + '"'
        new_img.append(new_i)
    re_imga30 = re.findall('value="(.*?)"', str(content))
    for i in re_imga30:
        new_i = 'value="' + i + '"'
        new_img.append(new_i)
    re_imga31 = re.findall('type="(.*?)"', str(content))
    for i in re_imga31:
        new_i = 'type="' + i + '"'
        new_img.append(new_i)
    re_imga32 = re.findall('textvalue="(.*?)"', str(content))
    for i in re_imga32:
        new_i = 'textvalue="' + i + '"'
        new_img.append(new_i)
    re_imga33 = re.findall('data-ratio="(.*?)"', str(content))
    for i in re_imga33:
        new_i = 'data-ratio="' + i + '"'
        new_img.append(new_i)
    re_imga34 = re.findall('data-s="(.*?)"', str(content))
    for i in re_imga34:
        new_i = 'data-s="' + i + '"'
        new_img.append(new_i)
    re_imga35 = re.findall('data-src="(.*?)"', str(content))
    for i in re_imga35:
        new_i = 'data-src="' + i + '"'
        new_img.append(new_i)
    re_imga36 = re.findall('data-type="(.*?)"', str(content))
    for i in re_imga36:
        new_i = 'data-type="' + i + '"'
        new_img.append(new_i)
    re_imga37 = re.findall('data-w="(.*?)"', str(content))
    for i in re_imga37:
        new_i = 'data-w="' + i + '"'
        new_img.append(new_i)
    re_imga38 = re.findall('id="(.*?)"', str(content))
    for i in re_imga38:
        new_i = 'id="' + i + '"'
        new_img.append(new_i)
    re_imga39 = re.findall('width="(.*?)"', str(content))
    for i in re_imga39:
        new_i = 'width="' + i + '"'
        new_img.append(new_i)
    re_imga40 = re.findall('data-catchresult="(.*?)"', str(content))
    for i in re_imga40:
        new_i = 'data-catchresult="' + i + '"'
        new_img.append(new_i)
    re_imga41 = re.findall('data-fail="(.*?)"', str(content))
    for i in re_imga41:
        new_i = 'data-fail="' + i + '"'
        new_img.append(new_i)
    re_imga42 = re.findall('data-ratio="(.*?)"', str(content))
    for i in re_imga42:
        new_i = 'data-ratio="' + i + '"'
        new_img.append(new_i)
    re_imga43 = re.findall('data-s="(.*?)"', str(content))
    for i in re_imga43:
        new_i = 'data-s="' + i + '"'
        new_img.append(new_i)
    re_imga44 = re.findall('srcset="(.*?)"', str(content))
    for i in re_imga44:
        new_i = 'srcset="' + i + '"'
        new_img.append(new_i)
    re_imga45 = re.findall('data-cmd="(.*?)"', str(content))
    for i in re_imga45:
        new_i = 'data-cmd="' + i + '"'
        new_img.append(new_i)
    re_imga46 = re.findall('wah-hotarea="(.*?)"', str(content))
    for i in re_imga46:
        new_i = 'wah-hotarea="' + i + '"'
        new_img.append(new_i)
    re_imga47 = re.findall('content="(.*?)"', str(content))
    for i in re_imga47:
        new_i = 'content="' + i + '"'
        new_img.append(new_i)
    re_imga48 = re.findall('http-equiv="(.*?)"', str(content))
    for i in re_imga48:
        new_i = 'http-equiv="' + i + '"'
        new_img.append(new_i)
    re_imga49 = re.findall('charset="(.*?)"', str(content))
    for i in re_imga49:
        new_i = 'charset="' + i + '"'
        new_img.append(new_i)
    re_imga50 = re.findall('word_img="(.*?)"', str(content))
    for i in re_imga50:
        new_i = 'word_img="' + i + '"'
        new_img.append(new_i)
    re_imga51 = re.findall('complete="(.*?)"', str(content))
    for i in re_imga51:
        new_i = 'complete="' + i + '"'
        new_img.append(new_i)
    re_imga52 = re.findall('align="(.*?)"', str(content))
    for i in re_imga52:
        new_i = 'align="' + i + '"'
        new_img.append(new_i)
    gather_re = list(set(new_img))
    gather_re.sort(key=new_img.index)
    # print(gather_re)
    for string in gather_re:
        content = str(content).replace('picname=\'title=""\'', '').replace(string, "")

    p_re = re.compile(r'<p.*?>')
    tb_re = re.compile(r'<table.*?>')
    span_re = re.compile(r'<span.*?>')
    tr_re = re.compile(r'<tr.*?>')
    td_re = re.compile(r'<td.*?>')
    h_re = re.compile(r'<h4.*?>')
    ol_re = re.compile(r'<ol.*?>')
    strong_re = re.compile(r'<strong.*?>')
    section_re = re.compile(r'<section.*?>')
    ucapcontent_re = re.compile(r'<ucapcontent.*?>')
    re_comment = re.compile('<!--[^>]*-->')
    re_comment2 = re.compile(r'<!-[\s\S]*?-->')
    re_href = re.compile(r'href="javascript:void\(0\);"')
    re_href2 = re.compile(r'href="#"')
    re_page = re.compile(r'@page.*?Section1 }')
    re_TRS_Editor = re.compile(r'.TRS_Editor.*?}')

    content = html.remove_tags(str(content), ("div", "font", "iframe", "video"), encoding="utf-8")
    content = p_re.sub('<p>', str(content))
    content = tb_re.sub('<table>', str(content))
    content = span_re.sub('<span>', str(content))
    content = tr_re.sub('<tr>', str(content))
    content = td_re.sub('<td>', str(content))
    content = h_re.sub('<h4>', str(content))
    content = ol_re.sub('<ol>', str(content))
    content = strong_re.sub('<strong>', str(content))
    content = section_re.sub('<section>', str(content))
    content = ucapcontent_re.sub('<ucapcontent>', str(content))
    content = re_comment.sub('', str(content))
    content = re_comment2.sub('', str(content))
    content = re_href.sub('', str(content))
    content = re_href2.sub('', str(content))
    content = re_page.sub('', str(content))
    content = re_TRS_Editor.sub('', str(content))
    content = re.sub('\n', '', str(content))
    # print(content)
    content = content.replace('data-', '')
    return content


def get_TP(soup, content_voice, new_url, annex_voice):
    """判断内容是否有图片或者内容"""
    db_host = "192.168.1.246"
    db_user = "Enterprise"
    db_pwd = "123456"
    db_port = 3306
    db_name = "picture_file"
    conn = pymysql.connect(host=db_host, user=db_user, password=db_pwd, port=db_port, db=db_name, autocommit=True)
    cur = conn.cursor()
    if annex_voice and annex_voice != '':
        fj_url = soup.select(annex_voice + ' a')
        fjsoup = soup.select(annex_voice)
    else:
        fj_url = soup.select(content_voice + ' a')
        fjsoup = soup.select(content_voice)
    img = soup.select(content_voice + ' img')
    fj_list = []
    get_id = re.findall(r'href="(.*?)"', str(fjsoup))
    if img or fj_url:
        print('有需要存储的文件')
        Sql = "select url from download WHERE url= '%s' " % new_url
        # 执行SQL语句
        cur.execute(Sql)
        LastGetId = cur.fetchall()
        if not LastGetId:
            today = str(datetime.datetime.now())[:-3]
            sql = "INSERT INTO download(url, Creation_time, expression) VALUES (%s, %s, %s)"
            if annex_voice and annex_voice != '':
                param = (new_url, today, annex_voice)
            else:
                param = (new_url, today, content_voice)
            try:
                # 执行sql语句
                conn.ping(reconnect=True)
                cur.execute(sql, param)
                # 提交到数据库执行
                # conn.commit()
                print('数据存储成功', )
            except Exception as e:
                print('数据存储失败', )
                print('数据存储报错：', e)
                # 发生错误时回滚
                conn.rollback()
    elif get_id:
        for i in get_id:
            if i.split('.')[-1] in ['docx', 'png', 'doc', 'pdf', 'xlsx', 'xls', 'zip', 'rtf',
                                    'jpg', 'rar', 'tif', 'ppt', 'mp4', 'asp', 'PDF', 'wps', 'flv']:
                fj_list.append(i)
                break
        print('有需要存储的文件')
        Sql = "select url from download WHERE url= '%s' " % new_url
        # 执行SQL语句
        cur.execute(Sql)
        LastGetId = cur.fetchall()
        if not LastGetId:
            today = str(datetime.datetime.now())[:-3]
            sql = "INSERT INTO download(url, Creation_time, expression) VALUES (%s, %s, %s)"
            param = (new_url, today, '')
            try:
                # 执行sql语句
                conn.ping(reconnect=True)
                cur.execute(sql, param)
                # 提交到数据库执行
                conn.commit()
                print('数据存储成功', )
            except Exception as e:
                print('数据存储失败', )
                print('数据存储报错：', e)
                # 发生错误时回滚
                conn.rollback()
        # 关闭数据库连接
    cur.close()
    conn.close()


def Store_data(new_url, title, source, docnum, Time, content, num, area, ly, url):
    """存储数据到Mysql"""
    global province, city, county
    db_host = "askci-db.rwlb.rds.aliyuncs.com"
    db_user = "datauser_collect"
    db_pwd = "uPTZ5y@xNy8PhEeR"
    db_port = 3306
    db_name = "policydata"
    conn = pymysql.connect(host=db_host, user=db_user, password=db_pwd, port=db_port, db=db_name,
                           autocommit=True)
    cur = conn.cursor()
    # SQL 插入语句
    today = str(datetime.datetime.now())[:-3]
    if area == '':
        province = '国家级'
        city = '-'
        county = '-'
    else:
        for s in province_list:
            if s in area:
                province = s
                if '市' in area:
                    city = re.findall(f'{province}(.*?)市', str(area))[0] + '市'
                    if '区' in area or '县' in area:
                        county = area.rsplit('市', 1)[-1]
                    else:
                        county = '-'
                else:
                    city = '-'
                    county = '-'
                break
    # SQL 插入语句
    INsql = "INSERT INTO Government_news (Original_url, Publish_link, title, Department, dispatch, source, Release_T, substance, Creation_time, province, city, area) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    param = (url, new_url, title, source, docnum, ly, Time, content, today, province, city, county)
    try:
        # 执行sql语句
        cur.execute(INsql, param)
        # 提交到数据库执行
        # SJK.commit()
        report = '第' + str(num) + '条数据存储成功'
        print(report)
    except Exception as e:
        report = '第' + str(num) + '条数据存储失败, 报错：' + str(e)
        print(report)
        # 发生错误时回滚
        conn.rollback()
    # 关闭数据库连接
    cur.close()
    conn.close()
    print()


def start_object():
    record = get_data()
    # print(record)
    temp = func(record, 2254)
    thread_list = []
    print(len(temp))
    for i in temp:
        print(i)
        t = threading.Thread(target=Run, args=(i,))
        # t.setDaemon(True)
        t.daemon = True
        thread_list.append(t)
    for t in thread_list:
        t.start()
        time.sleep(5)
    for t in thread_list:
        t.join()


def job1_task():
    threading.Thread(target=start_object).start()


def job2_task():
    record = get_data()
    if record:
        t1 = threading.Thread(target=Run, args=(record,))
        # # 设置线程保护
        t1.daemon = True
        # 启动子线程
        t1.start()
        t1.join()


def Time_object():
    # schedule.every(5).minutes.do(job1_task)
    # schedule.every(1).seconds.do(job1_task)
    schedule.every().day.at('15:43').do(job1_task)
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    print(' ' * 38 + '======程序运行======')
    while True:
        try:
            # Time_object()
            job2_task()
        except:
            pass

