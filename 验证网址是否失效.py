"""
#!/usr/bin/env python
# -*- coding:utf-8 -*-
@File : 验证网址是否失效.py
@Author : Zeng
@Time : 2023/6/2 15:29
"""
import re

import requests
from bs4 import BeautifulSoup
import time
import pymysql
import urllib3
from selenium import webdriver
urllib3.disable_warnings()

DBHOST = "askci-db.rwlb.rds.aliyuncs.com"
DBUSER = "datauser_collect"
DBPASS = "uPTZ5y@xNy8PhEeR"
DBNAME = "collectdata"
try:
    conn = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPASS, database=DBNAME)
    print("数据库成功连接")
except pymysql.Error as e:
    print("数据库连接失败")

def run():
    cur = conn.cursor()
    # selsql = 'SELECT PolicySourceUrl from policysource WHERE add_num = 0'
    selsql = "SELECT PolicySourceUrl from policysource WHERE add_num = 0 and Regionid like '%安徽%'"
    cur.execute(selsql)  # 执行sql语句
    results = cur.fetchall()  # 将查询结果返回成一个元组
    for _url in results:
        print(_url[0])
        url = _url[0]
        time.sleep(0.1)
        try:
            res = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}, timeout=30, verify=False)
            res.encoding = 'utf-8'
            if res.status_code == 521:
                options = webdriver.EdgeOptions()
                options.add_argument("--enable-features=NetworkServiceInProcess")
                options.add_argument("headless")
                options.add_argument("--disable-gpu")
                options.add_experimental_option('useAutomationExtension', False)
                options.add_experimental_option('excludeSwitches', ['enable-automation'])
                options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
                options.add_argument('--disable-blink-features=AutomationControlled')
                driver = webdriver.Edge(options=options)
                driver.get(url)
                driver.implicitly_wait(10)
                time.sleep(3)
                soup = driver.page_source
                content = re.findall('目录id:(.*?),不存在.', str(soup))
            else:
                soup = res.text
                content = re.findall('目录id:(.*?),不存在.', str(soup))
            # _content = f'目录id:{content},不存在.'
            print(content)
            if content:
            # if res.status_code == 404 or '无效的访问地址' in res.text:
                print('404 Not Found')
                up_sql = "UPDATE PolicySource SET LinkExpression = '%s' WHERE PolicySourceUrl = '%s'" % ('404 Not Found', url)
                conn.ping(reconnect=True)
                cur.execute(up_sql)  # 执行sql语句
                conn.commit()  # 提交到数据库执行
                print('update success')
        except:
            pass
    cur.close()  # 关闭游标对象，该游标对象无法再使用
    conn.close()  # 关闭数据库连接


run()
