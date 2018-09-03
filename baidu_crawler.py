# -*- coding:utf-8 -*-
import sys
import requests
from lxml import etree
import random
import config as cfg
import pymysql as mdb 
 
def get_proxies( ):
    ip_list = []

    # 连接数据库
    conn = mdb.connect(cfg.host, cfg.user, cfg.passwd, cfg.DB_NAME)
    cursor = conn.cursor()

    # 检查数据表中是否有数据
    try:
        cursor.execute('SELECT * FROM %s ' % cfg.TABLE_NAME)

        # 提取数据
        result = cursor.fetchall()

        # 若表里有数据　直接返回，没有则抓取再返回
        if len(result):
            for item in result:
                ip_list.append(item[0])       
    except Exception as e:
        print ("从数据库获取ip失败！")
    finally:
        cursor.close()
        conn.close()

    return ip_list
 

"""
================================================
 Extract text from the result of BaiDu search
================================================
"""


def download_html(keywords, proxy):
    """
    抓取网页
    """
    # 抓取参数 https://www.baidu.com/s?wd=testRequest
    key = {'wd': keywords}
    
    # 请求Header
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv:11.0 cb) like Gecko'}

    proxy = {'http': 'http://'+proxy}

    # 抓取数据内容
    web_content = requests.get("https://www.baidu.com/s?", params=key, headers=headers, proxies=proxy, timeout=4)

    return web_content.text


def html_parser(html):
    """
    解析html
    """
    # 设置提取数据正则
    path_cn = "//div[@id='content_left']//div[@class='c-abstract']/text()"
    path_en = "//div[@id='content_left']//div[@class='c-abstract c-abstract-en']/text()"

    # 提取数据
    tree = etree.HTML(html)
    results_cn = tree.xpath(path_cn)
    results_en = tree.xpath(path_en)
    text_cn = [line.strip() for line in results_cn]
    text_en = [line.strip() for line in results_en]

    # 设置返回结果
    text_str = ''

    # 提取数据
    if len(text_cn) != 0 or len(text_en) != 0:
        # 提取中文
        if len(text_cn):
            for i in text_cn:
                text_str += (i.strip())
        # 提取英文
        if len(text_en) != 0:
            for i in text_en:
                text_str += (i.strip())
    # 返回结果
    return text_str


def extract_all_text(keyword_dict, keyword_text):
    """
    存储结果
    """
    useful_proxies = {}
    
    try:
        # 获取代理IP数据
        for ip in get_proxies():
            useful_proxies[ip] = 0
        print( "总共：" + str(len(useful_proxies)) + 'IP可用')
    except OSError:
        print ("获取代理ip时出错！")

    cn = open(keyword_dict, 'r', encoding='UTF-8')
    with open(keyword_text, 'w', encoding='UTF-8') as ct:
        # 逐行读取关键词
        for line in cn:
            # 设置随机代理
            proxy = random.choice(list(useful_proxies))
            print( "change proxies: " + proxy)

            content = ''
            try:
                content = download_html(line.strip(), proxy)
            except OSError:
                # 超过3次则删除此proxy
                useful_proxies[proxy] += 1
                if useful_proxies[proxy] > 3:
                    useful_proxies.remove(proxy)
                # 再抓一次
                proxy = random.choice(list(useful_proxies))
                content = download_html(line.strip(), proxy)

            raw_text = html_parser(content)
            raw_text = raw_text.replace('\n', '||')
            print (raw_text)

            # 写入数据到文件
            ct.write(line.strip()+':\t'+raw_text+'\n')

        ct.close()
        cn.close()


def main():
    # 抓取搜索关键词
    keyword_dict = 'data/samples.txt'
    # 抓取存取结果
    keyword_text = 'data/results.txt'

    # 抓取数据
    
    extract_all_text(keyword_dict, keyword_text)

if __name__ == '__main__':
    main()
