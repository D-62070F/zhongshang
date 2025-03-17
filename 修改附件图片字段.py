"""
#!/usr/bin/env python
# -*- coding:utf-8 -*-
@File : 修改附件图片字段.py
@Author : Zeng
@Time : 2023/7/6 14:24
"""
import pymysql
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

db_host = "askci-db.rwlb.rds.aliyuncs.com"
db_user = "datauser_collect"
db_pwd = "uPTZ5y@xNy8PhEeR"
db_port = 3306
db_name = "collectdata"
conn = pymysql.connect(host=db_host, user=db_user, password=db_pwd, port=db_port, db=db_name, autocommit=True)
cur = conn.cursor()


def go():
    selsql = 'select url from download WHERE judge is null'
    cur.execute(selsql)  # 执行sql语句
    results = cur.fetchall()  # 将查询结果返回成一个元组
    # cur.close()  # 关闭游标对象，该游标对象无法再使用
    # conn.close()  # 关闭数据库连接
    urls = results
    for i in urls:
        _url = i[0]
        print(_url)
        try:
            res = requests.get(_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}, timeout=10, verify=False)
            if res.status_code == 404:
                delsql = f'DELETE from download WHERE url = "{_url}"'
                cur.execute(delsql)
        except Exception as result:
            print("异常处理", result)
            print(11111111111)
            pass
        # _selsql = f'SELECT Original_url FROM policydata.`government_news` WHERE Publish_link = "{_url}"'
        # cur.execute(_selsql)  # 执行sql语句
        # _results = cur.fetchall()  # 将查询结果返回成一个元组
        # if _results:
        #     Original_url = _results[0][0]
        #     if Original_url == '':
        #         pass
        #     else:
        #         __selsql = f'SELECT ContentExpression, AnnexExpression FROM `policysource` WHERE PolicySourceUrl = "{Original_url}"'
        #         cur.execute(__selsql)  # 执行sql语句
        #         __results = cur.fetchall()  # 将查询结果返回成一个元组
        #         if __results:
        #             print(_url)
        #             print(__results[0])
        #             if __results[0][1] == '':
        #                 upsql = f"UPDATE download set expression = '{__results[0][0]}' WHERE url = '{_url}'"
        #                 cur.execute(upsql)
        #             else:
        #                 upsql = f"UPDATE download set expression = '{__results[0][1]}' WHERE url = '{_url}'"
        #                 cur.execute(upsql)
        #             print(upsql, '\n')


go()
