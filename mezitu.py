# -*- coding:utf-8 -*-

# coding: utf-8
import requests
from lxml import etree
import urllib
import random
import os 
import time
class MZitu():
    def __init__(self,baseURL,pages):
        self.baseURL = baseURL
        self.pages = pages
        self.UserAgent_List = [
                            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
                            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
                            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
                            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
                            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
                            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
                            "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
                            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
                            "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
                            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
                            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
                            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
                            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
                            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
                            "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
                            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
                            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
                            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"]

        self.head = {'Accept':'Accept=text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                     'Accept-Encoding':'gzip, deflate, sdch',
                     'Accept-Language':'zh-CN,zh;q=0.8',
                     'Connection':'keep-alive',
                     'Cookie':'Hm_lvt_dbc355aef238b6c32b43eacbbf161c3c=1509151839; Hm_lpvt_dbc355aef238b6c32b43eacbbf161c3c=1509151861',
                     'Host':'http://www.mzitu.com',
                     'Referer':'http://www.mzitu.com/page/1',
                     'Upgrade-Insecure-Requests':'1',
                     'User-Agent':random.choice(self.UserAgent_List)
                     }
    def header(self,referer):
        headers = {
            'Host': 'i.meizitu.net',
            'Pragma': 'no-cache',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/59.0.3071.115 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': '{}'.format(referer),
        }
        return headers   
    
    def getURL(self):
        urlMain = "http://www.mzitu.com/"
        resMain = requests.get(urlMain,headers = self.head)
        resMain.encoding = 'utf-8'
        selectorMain = etree.HTML(resMain.text)
        urls = []
        for url in selectorMain.xpath('//*[@id="pins"]//li/a/@href'):
            urls.append(url)
        return urls
   
    def getonepic(self,url):
        res_pic = requests.get(url,headers = self.head)
        res_pic.encoding = 'utf-8'
        selector_pic = etree.HTML(res_pic.text)
        pic = selector_pic.xpath('/html/body/div[2]/div[1]/div[3]/p/a/img/@src')
        return pic
    
    def geteverypageURL(self,urlpic,num):
        url = urlpic+"/"+str(num)
        return url
    def getTitle(self,url):
        res = requests.get(url)
        content=[]
        selector_sin = etree.HTML(res.text)
        content.append(selector_sin.xpath('//h2[@class="main-title"]')[0].text)
        content.append(selector_sin.xpath('/html/body/div[2]/div[1]/div[4]/a[5]/span')[0].text)  
  
        return content
    
    def downloadpic(self):
        urls = self.getURL()
        for i in range(0,len(urls)):
            print(urls[i])
            title = self.getTitle(str(urls[i]))
            time.sleep(3)
            dirName = u"【%sP】%s" % (str(title[1]),title[0])
            os.mkdir(dirName)    
            k = 1
            for n in range(0,int(title[1])+1):
                oneurl = self.geteverypageURL(urls[i],n)
                time.sleep(1)
                pic = self.getonepic(oneurl)
                time.sleep(1)
                print(pic[0])
                filename = '%s/%s/%s.jpg' % (os.path.abspath('.'), dirName, k)
                with open(filename, "wb") as jpg:
                    jpg.write(requests.get(pic[0],headers = self.header(pic[0])).content)
                    time.sleep(0.5)
                k += 1
baseURL = "http://www.mzitu.com/"        
tu = MZitu(baseURL,1)
tu.downloadpic()
tu.getURL()