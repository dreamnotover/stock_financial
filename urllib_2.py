# -*- coding:utf-8 -*-

from lxml import etree
import pymysql as mdb
import datetime
from selenium import webdriver

 
def get_proxy_list(url,url_xpath ):
    '''
    返回抓取到代理的列表
    整个爬虫的关键
    '''
    options = webdriver.ChromeOptions()  
   
    options.add_argument("--headless")  
    browser = webdriver.Chrome(chrome_options = options,executable_path='D:\\chromedriver.exe')
    browser.implicitly_wait(30)
    browser.maximize_window()
   
    browser.get(url)
    browser.implicitly_wait(3)
    # 找到代理table的位置
    elements = browser.find_elements_by_xpath(url_xpath)
    return  elements 

url='http://emweb.securities.eastmoney.com/OperationsRequired/Index?type=web&code=SZ300059'
url_xpath='//*[@id="templateDiv1"]/div[7]/div[2]/div'
elements=get_proxy_list(url,url_xpath )