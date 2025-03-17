"""
#!/usr/bin/env python
# -*- coding:utf-8 -*-
@File : GUI.py
@Author : Zeng
@Time : 2022/7/19 14:07
"""
import datetime
import random
import socket
import time
from tkinter import *
import re
import pymysql
import requests
import urllib3
from bs4 import BeautifulSoup
import tkinter as tk
from w3lib import html

global sf_input, sq_input, dq_input, url_input, PJ_input, ys_input, LJ_input, BT_input, SJ_input, NR_input, text, url_list, origin, ly, fwzh

user_agents = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36 ",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.2 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1467.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1464.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.60 Safari/537.17",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.14 (KHTML, like Gecko) Chrome/24.0.1292.0 Safari/537.14"
]
user_agents = random.choice(user_agents)


def LJ_sql():
    db_host = "192.168.1.246"
    db_user = "government"
    db_pwd = "123123"
    db_port = 3306
    db_name = "government_data"
    conn = pymysql.connect(host=db_host, user=db_user, password=db_pwd, port=db_port, db=db_name, autocommit=True)
    return conn


def Crawl_content():
    """
    判断网页是否有翻页
    输入获取内容的表达式
    """
    A = sf_input.get()
    if A:
        B = sq_input.get()
        if B == '':
            B = '-'
        C = dq_input.get()
        if C == '':
            C = '-'
        # 设置HTTP或Socket超时，来防止爬虫爬取某个页面时间过长
        global url_list, ly
        socket.setdefaulttimeout(20)
        # 证书认证及警告的禁用
        urllib3.disable_warnings()
        url_list = []  # 需要抓取的Url集合
        url = url_input.get()
        p = re.compile(r'(\d+)\.')
        judge = ys_input.get()  # 输入翻页表达式
        entry = LJ_input.get()  # 输入获取链接表达式
        if url:
            if entry:
                if judge:
                    report = '该网页需要翻页抓取'
                    text.insert(END, report)
                    text.see(END)
                    text.update()
                    for i in range(1, int(judge) + 1):
                        url = p.sub(str(i) + '.', str(url))
                        get_Url(url, url_list, entry)
                        ly = get_origin(url)
                else:
                    report = '该网页不需要翻页抓取'
                    text.insert(END, report)
                    text.see(END)
                    text.update()
                    get_Url(url, url_list, entry)
                    ly = get_origin(url)
            else:
                report = '还未填入获取详情链接表达式，请输入后再爬取'
                text.insert(END, report)
                text.see(END)
                text.update()
        else:
            report = '  ' * 28 + '请填入要爬取的网页链接'
            text.insert(END, report)
            text.see(END)
            text.update()
        num = 0
        report = '一共有', len(url_list), '个网址需要抓取'
        text.insert(END, report)
        text.see(END)
        text.update()
        nurl_list = ',   '.join(url_list)
        if url_list[0][0:4] == 'http':
            for i in url_list:
                num += 1
                report = ('正在爬取第', num, '个网址')
                text.insert(END, report)
                # 文本框向下滚动
                text.see(END)
                # 更新
                text.update()
                get_shuju(i, num, A, B, C, ly)
                # break
        else:
            report = nurl_list
            text.insert(END, report)
            text.see(END)
            text.update()
            report = '该链接不完整，需要拼接获得完整链接'
            text.insert(END, report)
            text.see(END)
            text.update()
            ID_Splicing = PJ_input.get()
            if ID_Splicing:
                for i in url_list:
                    new_url = ID_Splicing + i[1:]
                    num += 1
                    report = ('正在爬取第', num, '个网址')
                    text.insert(END, report)
                    text.see(END)
                    text.update()
                    get_shuju(new_url, num, A, B, C, ly)
            else:
                report = '补全正确链接才能进行爬取'
                text.insert(END, report)
                text.see(END)
                text.update()
    else:
        report = '  ' * 28 + '输入完整的地区再进行爬取'
        text.insert(END, report)
        text.see(END)
        text.update()


def get_Url(url, url_list, entry):
    """
    不翻页获取详情连接
    """
    res = requests.get(url, headers={'User-Agent': user_agents}, timeout=20, verify=False)
    if int(requests.get(url).status_code) == 200:  # 判断请求状态码
        res.encoding = 'utf-8'  # 设置编码
        soup = BeautifulSoup(res.text, 'lxml')
        uls = soup.select(entry + ' a')
        for ul in uls:
            href = ul.get('href')
            if href[0:4] == 'http':  # 判断链接是否为完整(以http开头）
                # 判断是否为网页连接
                if str(href).split('.')[-1] not in ['docx', 'png', 'doc', 'pdf', 'xlsx', 'xls', 'zip', 'rtf', 'jpg',
                                                    'rar', 'tif', 'ppt', 'mp4', 'asp', 'PDF', 'wps', 'flv']:
                    url_list.append(href)
                else:
                    report = '----------------此链接异常，不是网页url链接----------------'
                    # 添加数据
                    text.insert(END, report)
                    text.see(END)
                    text.update()
            else:
                get_id = re.findall(r'/[a-zA-Z0-9]\S+|[a-zA-Z0-9]\S+', str(href))  # 不完整以正则表达式获取链接
                if get_id:
                    if get_id[0].split('.')[-1] not in ['docx', 'png', 'doc', 'pdf', 'xlsx', 'xls', 'zip', 'rtf',
                                                        'jpg', 'rar', 'tif', 'ppt', 'mp4', 'asp', 'PDF', 'wps',
                                                        'flv']:
                        url_list.append(get_id[0])
                    else:
                        report = '----------------此链接异常，不是网页url链接----------------'
                        text.insert(END, report)
                        text.see(END)
                        text.update()
                else:
                    report = '----------------没找到正确的url链接----------------'
                    text.insert(END, report)
                    text.see(END)
                    text.update()
    else:
        report = '该网站请求失败已跳过爬取'
        text.insert(END, report)
        text.see(END)
        text.update()
    return url_list


def get_origin(url):
    """获取文章来源"""
    global origin
    try:
        try:
            res = requests.get(url, headers={'User-Agent': user_agents}, timeout=20, verify=False)
            if int(requests.get(url).status_code) == 200:  # 判断请求状态码
                res.encoding = 'utf-8'  # 设置编码
                soup = BeautifulSoup(res.text, 'lxml')
                origin = re.findall('<title>(.*?) - .*?</title>', str(soup))[0]
        except:
            origin = '-'
        return origin
    except Exception as e:
        YC = '来源' + str(e)
        text.insert(END, YC)
        text.see(END)
        text.update()


def get_shuju(i, num, A, B, C, ly):
    """
    :param i: 详情页链接
    :param num: 变量记录存储数目
    :param title_voice: 获取标题表达式
    :param time_voice: 获取时间表达式
    :param content_voice: 获取内容表达式
    获取时间、标题、内容；保存图片附件以及数据保存到数据库
    """
    try:
        report = ('链接： ' + i)
        text.insert(END, report)
        text.see(END)
        text.update()
        response = requests.get(i, headers={'User-Agent': user_agents})
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        title = get_BT(soup)  # 获取标题
        source = get_LY(soup)   # 获取发布机构
        docnum = get_Document(soup)   # 获取发文字号
        Time = get_SJ(soup, response)  # 获取时间
        content = get_NR(soup)  # 获取内容
        if content == 0:
            report = '  ' * 28 + '报错了不能存储'
            text.insert(END, report)
            text.see(END)
            text.update()
        else:
            get_TP(soup, i)  # 保存图片、附件
            Store_data(i, title, Time, content, num, A, B, C, source, ly, docnum)  # 存储数据
    except:
        pass
    report = ('*' * 88)
    text.insert(END, report)
    text.see(END)
    text.update()


def get_BT(soup):
    """获取标题"""
    try:
        time_voice = BT_input.get()
        try:
            # Title = soup.xpath(time_voice)[0].strip()
            Title = soup.select(time_voice)[0].text.strip()
        except:
            Title = re.findall(r'meta content="(.*?)" name="ArticleTitle"/>', str(soup))[0].strip()
        report = str('标题： ' + Title)
        text.insert(END, report)
        text.see(END)
        text.update()
        return Title
    except Exception as e:
        YC = '爬取标题报错' + str(e)
        text.insert(END, YC)
        text.see(END)
        text.update()


def get_LY(soup):
    """获取发布机构"""
    try:
        try:
            Source = re.findall('<meta content="(.*?)" name="ContentSource"/>', str(soup))[0]
        except:
            Source = '-'
        report = str('发布机构： ' + Source)
        text.insert(END, report)
        text.see(END)
        text.update()
        return Source
    except Exception as e:
        YC = '发布机构' + str(e)
        text.insert(END, YC)
        text.see(END)
        text.update()


def get_Document(soup):
    """获取发文字号"""
    global fwzh
    try:
        try:
            qw = str(soup.text).strip().replace(' ', '').replace('　', '')
            wenhao = re.findall('文号：[\n|\t](.*?)号', str(qw))
            if wenhao:
                fwzh = wenhao[0] + '号'
            else:
                fwzh = '-'
        except:
            fwzh = '-'
        report = str('发文字号： ' + fwzh)
        text.insert(END, report)
        text.see(END)
        text.update()
        return fwzh
    except Exception as e:
        YC = '发文字号' + str(e)
        text.insert(END, YC)
        text.see(END)
        text.update()


def get_SJ(soup, response):
    """获取时间"""
    try:
        time_voice = SJ_input.get()
        try:
            FBtime = soup.select(time_voice)[0].text.strip()
            Time_show = str(FBtime).replace('年', '-').replace('月', '-').replace('日', '-') \
                .replace('/', '-').replace('.', '-').replace('\n', '').replace(' ', '')
            Time_RE = re.findall("(?P<YYYY>\\d{4})-(?P<MM>\\d{1,2})-(?P<dd>\\d{1,2})", str(Time_show))[0]
            Time_RE1 = "-".join(Time_RE)
        except:
            Time_RE = re.findall("(?P<YYYY>\\d{4})-(?P<MM>\\d{1,2})-(?P<dd>\\d{1,2})", str(response.text))[0]
            Time_RE1 = "-".join(Time_RE)
        report = str('发布时间： ' + Time_RE1)
        text.insert(END, report)
        text.see(END)
        text.update()
        return Time_RE1
    except Exception as e:
        YC = '爬取时间报错' + str(e)
        text.insert(END, YC)
        text.see(END)
        text.update()


def get_NR(soup):
    """获取内容"""
    try:
        Now_time = str(datetime.datetime.now())[:10] + '/'
        imgs = soup.find_all("img")
        for img in imgs:
            if img.get('src'):
                img["src"] = '/upload/PictureUpload/' + Now_time + img["src"].split("/")[-1]
        content_voice = NR_input.get()
        FB_content = soup.select(content_voice)[0]
        [s.extract() for s in FB_content('script')]
        report = str('发布内容： ' + FB_content.text[:168].strip())
        clean_FB_content = wash(FB_content)
        text.insert(END, report)
        text.see(END)
        text.update()
        return clean_FB_content
    except Exception as e:
        YC = '爬取内容报错' + str(e)
        text.insert(END, YC)
        text.see(END)
        text.update()
        return 0


def wash(content):
    # gather_re = []
    WJ_hz = ['zip', 'txt', 'doc', 'xls', 'ppt', 'docx', 'xlsx', 'pptx', 'pdf', 'tiff', 'swf',
             'rar', 'jpg', 'tif', 'png', 'ofd', 'PDF', 'DOC', 'XLS', 'wps', 'et']
    try:
        for a in content.findAll('a'):
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
    re_imga10 = re.findall('width="(.*?)"', str(content))
    for i in re_imga10:
        new_i = 'width="' + i + '"'
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
    re_imga23 = re.findall('id="(.*?)"', str(content))
    for i in re_imga23:
        new_i = 'id="' + i + '"'
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
    gather_re = list(set(new_img))
    gather_re.sort(key=new_img.index)
    # print(gather_re)
    for string in gather_re:
        content = str(content).replace('picname=\'title=""\'', '').replace(string, "").replace('data-', '')

    p_re = re.compile(r'<p.*?>')
    tb_re = re.compile(r'<table.*?>')
    span_re = re.compile(r'<span.*?>')
    tr_re = re.compile(r'<tr.*?>')
    td_re = re.compile(r'<td.*?>')
    h_re = re.compile(r'<h4.*?>')
    ol_re = re.compile(r'<ol.*?>')
    re_comment = re.compile('<!--[^>]*-->')

    content = html.remove_tags(str(content), ("div", "font"), encoding="utf-8")
    content = p_re.sub('<p>', str(content))
    content = tb_re.sub('<table>', str(content))
    content = span_re.sub('<span>', str(content))
    content = tr_re.sub('<tr>', str(content))
    content = td_re.sub('<td>', str(content))
    content = h_re.sub('<h4>', str(content))
    content = ol_re.sub('<ol>', str(content))
    content = re_comment.sub('', str(content))
    content = re.sub('\n', '', str(content))
    # print(content)
    return content


def get_TP(soup, i):
    """判断内容是否有图片或者附件"""
    content_voice = NR_input.get()
    if content_voice:
        fj_url = soup.select(content_voice + ' a')
        img = soup.select(content_voice + ' img')
        if img or fj_url:
            db_host = "192.168.1.246"
            db_user = "government"
            db_pwd = "123123"
            db_port = 3306
            db_name = "picture_file"
            conn = pymysql.connect(host=db_host, user=db_user, password=db_pwd, port=db_port, db=db_name, autocommit=True)
            cur = conn.cursor()
            Sql = "select url from download WHERE url= '%s' " % (i)
            # 执行SQL语句
            cur.execute(Sql)
            LastGetId = cur.fetchall()
            if not LastGetId:
                report = '该网址有需要存储的文件'
                text.insert(END, report)
                text.see(END)
                text.update()
                # SQL 插入语句
                today = str(datetime.datetime.now())[:-3]
                sql = "INSERT INTO download(url, Creation_time) VALUES (%s, %s)"
                param = (i, today)
                try:
                    # 执行sql语句
                    cur.execute(sql, param)
                    # 提交到数据库执行
                    conn.commit()
                    report = '数据存储成功'
                    text.insert(END, report)
                    text.see(END)
                    text.update()
                except Exception as e:
                    report = '数据存储失败，报错：' + str(e)
                    text.insert(END, report)
                    text.see(END)
                    text.update()
                    # 发生错误时回滚
                    conn.rollback()
                # 关闭数据库连接
            conn.close()


def Store_data(i, title, Time, content, num, A, B, C, source, ly, docnum):
    """存储数据到Mysql"""
    SJK = LJ_sql()
    cur = SJK.cursor()
    today = str(datetime.datetime.now())[:-3]
    #   查询数据库是否已存储该网站数据
    Sql = "select Publish_link from test WHERE Publish_link= '%s' " % (i)
    cur.execute(Sql)
    LastGetId = cur.fetchall()
    time.sleep(0.5)
    if not LastGetId:
        # SQL 插入语句
        sql = "INSERT INTO test(Publish_link, Department, title, Release_T, substance, province, city, area, Creation_time, source, dispatch) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        param = (i, source, title, Time, content, A, B, C, today, ly, docnum)
        try:
            # 执行sql语句
            cur.execute(sql, param)
            # 提交到数据库执行
            SJK.commit()
            report = '第' + str(num) + '条数据存储成功'
            text.insert(END, report)
            text.see(END)
            text.update()
        except Exception as e:
            # print('第', num, '条数据存储失败', )
            # print('数据存储报错：', e)
            report = '第' + str(num) + '条数据存储失败, 报错：' + str(e)
            text.insert(END, report)
            text.see(END)
            text.update()
            # 发生错误时回滚
            SJK.rollback()
        # 关闭数据库连接
    SJK.close()


def cle():
    """定义一个函数，用于清空输入框的内容"""
    # text.delete(0, 'end')  # 从第一行清除到最后一行
    url_input.delete(0, 'end')
    PJ_input.delete(0, 'end')
    ys_input.delete(0, 'end')
    LJ_input.delete(0, 'end')
    BT_input.delete(0, 'end')
    SJ_input.delete(0, 'end')
    NR_input.delete(0, 'end')


def cle2():
    """定义一个函数，用于清空输出框的内容"""
    text.delete(0, 'end')  # 从第一行清除到最后一行



def main():
    global sf_input, sq_input, dq_input, url_input, PJ_input, ys_input, LJ_input, BT_input, SJ_input, NR_input, text
    # 创建空白窗口,作为主载体
    root = tk.Tk()
    root.title('爬虫工具-Zeng')
    # 窗口的大小，后面的加号是窗口在整个屏幕的位置    +398+279
    root.geometry('880x788')

    # 标签控件，窗口中放置文本组件
    Label(root, text='爬取的url: ', font=("楷体", 18), fg='black').grid(sticky=E)
    Label(root, text='拼接获取完整链接：', font=("宋体", 18), fg='black').grid(sticky=E)
    Label(root, text='要爬取的页数: ', font=("宋体", 18), fg='maroon').grid(sticky=E)
    Label(root, text='获取详情链接的表达式：', font=("宋体", 18), fg='black').grid(sticky=E)
    Label(root, text='获取标题的表达式：', font=("隶书", 18), fg='red').grid(sticky=E)
    Label(root, text='获取时间的表达式：', font=("隶书", 18), fg='red').grid(sticky=E)
    Label(root, text='获取内容的表达式：', font=("隶书", 18), fg='red').grid(sticky=E)
    Label(root, text="省:", font=("隶书", 13), fg='red').grid(row=3, column=2, sticky=E)
    Label(root, text="市:", font=("隶书", 13), fg='red').grid(row=4, column=2, sticky=E)
    Label(root, text="区:", font=("隶书", 13), fg='red').grid(row=5, column=2, sticky=E)

    sf_input = Entry(root)
    sf_input.grid(row=3, column=3, sticky=W)
    sq_input = Entry(root)
    sq_input.grid(row=4, column=3, sticky=W)
    dq_input = Entry(root)
    dq_input.grid(row=5, column=3, sticky=W)

    # 定位 pack包 place位置 grid是网格式的布局
    # Entry是可输入文本框
    url_input = Entry(root, font=("微软雅黑", 13))
    url_input.grid(row=0, column=1, sticky=W)
    PJ_input = Entry(root, font=("微软雅黑", 13))
    PJ_input.grid(row=1, column=1, sticky=W)
    ys_input = Entry(root, font=("微软雅黑", 13))
    ys_input.grid(row=2, column=1, sticky=W)
    LJ_input = Entry(root, font=("微软雅黑", 13))
    LJ_input.grid(row=3, column=1, sticky=W)
    BT_input = Entry(root, font=("微软雅黑", 13))
    BT_input.grid(row=4, column=1, sticky=W)
    SJ_input = Entry(root, font=("微软雅黑", 13))
    SJ_input.grid(row=5, column=1, sticky=W)
    NR_input = Entry(root, font=("微软雅黑", 13))
    NR_input.grid(row=6, column=1, sticky=W)

    # Label(root, text='测试', font=("微软雅黑", 10), fg='black').grid(row=3)
    # 列表控件
    # text = Text(root, font=('微软雅黑', 15), width=73, height=19)
    text = Listbox(root, font=('微软雅黑', 15), width=72, height=19)
    #   添加 "horizontal"（垂直滚动条）还是 "vertical"（水平滚动条）
    EventScrollBar2 = tk.Scrollbar(root, command=text.yview, orient="vertical")
    EventScrollBar2.grid(row=7, columnspan=4, sticky="nse")
    text.grid(row=7, columnspan=4)
    text.configure(yscrollcommand=EventScrollBar2.set)

    # Button(root, text='X', font=("微软雅黑", 13), command=xuanzeshi).grid(row=0, column=2, sticky=W)
    # 设置按钮 sticky对齐方式，N S W E
    Button(root, text='开始抓取', font=("微软雅黑", 13), command=Crawl_content).grid(row=0, column=3, sticky=NE)
    # 添加一个按钮，用于退出程序
    Button(root, text='退出', font=("微软雅黑", 13), command=root.quit).grid(row=1, column=3, sticky=E)
    # 添加一个按钮，用于触发清空输入框功能
    Button(root, text='清空输入', font=("微软雅黑", 13), command=cle).grid(row=2, column=3, sticky=E)
    # 添加一个按钮，用于触发清空文本输出框功能
    Button(root, text='清空文本', font=("微软雅黑", 13), command=cle2).grid(row=2, column=3, sticky=W)
    # 使得窗口一直存在
    mainloop()


main()

