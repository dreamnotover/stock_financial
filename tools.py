# -*- coding: utf-8 -*-	
import os
import requests
import re
import pymysql
from lxml import etree
import config as cfg
import logging
import  datetime
import json
# set up logging to file - see previous section for more details
basedir=os.path.dirname(os.path.realpath(__file__))
logfile="%s\\log\\st_%s.log" %(basedir,datetime.datetime.now().strftime("%Y-%m-%d"))   
logging.basicConfig(filename=logfile, level=logging.DEBUG,format='%(asctime)s  %(message)s')
query="INSERT INTO t_stock (symbol, name)values(%s,%s)on duplicate key update  name=values(name)"   
def stock_code(code,with_s=False,upper=False):
    code = code.lower()             #全部小写
    if with_s:                      #如果需要加上SH/SZ
        if code[0] != "s":          #如果第一个字符不是s
            if code[0]=="6" or code[0]=="9":        #如果第一个字符是6
                code = "sh"+code    #开头加上SH，上海代码以6开头
            else:                   #否则（开头不是6）
                code= "sz"+code     #代码前边加上SZ（深圳）
    else:                           #否则（要求不带SH/SZ）
        if code[0]=="s":            #如果第一个字符是S
            code = code[2:]          #把前边两个字符去掉
    if upper:                        #如果要求强制大写
        code = code.upper()          #那就强制大写
    if len(code)==6 or len(code)==8: #如果股票代码长度为6（有SH/SZ）或者8（无SH/SZ）
        return code                  #F返回处理过的股票代码
    else:                            #否则（长度不对
        return ""                    #返回空字符



#取得HTML数据，参数是URL网址，返回一个字符串，内容就是HTML的内容，如果不成功，返回空字符串
def GetHTMLText(url):
    #这就是最基本request对象用法，弄不懂没关系，异常，编码有点烦不是，抄
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""


#取得股票列表——东方财富
def get_stock_list_arr():
    #这就是所有股票代码的列表网址，东方财富的，可以复制到浏览器看下
    StockListUrl = "http://quote.eastmoney.com/stocklist.html"
    #存放代码的列表
    values=[]
    #调用刚才的函数，取得东方财富的代码列表网页，并全部用小写字母表达
    html = GetHTMLText(StockListUrl)
    s = html.lower()
    #这就是套路，照抄记住就行
    page = etree.HTML(s)
    if page==None:  #如果无内容，则返回
        return None
    #z找到所有带标签的内容，然后遍历，这里用到了xpath，非常方便的爬虫技巧
    href = page.xpath('//a')
    for i in href:
        try:
            s = i.text
            d = re.match(r"([\u4e00-\u9fff]+)\(([630][0]\d{4})\)",s)
            if len(d.groups())==2:
                value=[d.group(2),d.group(1)]         
                values.append(value)
        except:
            continue
    return values

#取得股票列表——东方财富
def get_stock_list():
    #这就是所有股票代码的列表网址，东方财富的，可以复制到浏览器看下
    StockListUrl = "http://quote.eastmoney.com/stocklist.html"
    #存放代码的列表
    StockList=[]
    #调用刚才的函数，取得东方财富的代码列表网页，并全部用小写字母表达
    html = GetHTMLText(StockListUrl)
    s = html.lower()
    #这就是套路，照抄记住就行
    page = etree.HTML(s)
    if page==None:  #如果无内容，则返回
        return None
    #z找到所有带标签的内容，然后遍历，这里用到了xpath，非常方便的爬虫技巧
    href = page.xpath('//a')
    for i in href:
        try:
            s = i.text
            d = re.findall(r"[630][09]\d{4}",s)
            if len(d)>0:
                StockList.append(d[0])
        except:
            continue
    StockList.append("999999")
    return StockList
 
def  insert_query(query,values):
    if  len(values) > 0 :
        sqlstr=json.JSONEncoder().encode(values)
        sqlstr=sqlstr.replace('[', '(').replace(']',')').replace('((', '(').replace('))',')')
        sqlstr= "INSERT INTO t_163_data (symbol, date, item_key, item_value) VALUES"+sqlstr+'on duplicate key update item_value=values(item_value)'
        logging.info( sqlstr) 
        connection = pymysql.connect(cfg.host, cfg.user, cfg.passwd, cfg.DB_NAME,charset='utf8')
        mycursor= connection.cursor()
        
        try:
            # Execute the SQL command
           
            mycursor.executemany(query, values)
            connection.commit()
            affected_rows = mycursor.rowcount
            if affected_rows:
                print("Number of rows affected : {}".format(affected_rows))
                 
            else:
                print('0 row  affected!')
                 
            
        except  Exception as e:
            #writeFile("Exeception occured:{}".format(e))
            print(("Exeception occured:{}".format(e)))
            
            connection.rollback()
        finally:
            mycursor.close()
            connection.close()
def get_fin_item( reportname):
    itemtype=dict()
    connection = pymysql.connect(cfg.host, cfg.user, cfg.passwd, cfg.DB_NAME,charset='utf8')
    mycursor= connection.cursor()            
    mycursor.execute('SELECT * FROM t_163_item WHERE `GROUP` = \'' + reportname + '\'')
    for row in mycursor:
        itemtype[row[2]] = row[0] 
    return  itemtype
# =============================================================================
# items= get_fin_item( '主要财务指标')  
# print(items)        
# =============================================================================
# =============================================================================
# 
# values=get_stock_list_arr()
# insert_query(query,values);
# =============================================================================
