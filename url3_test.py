# -*- coding: utf-8 -*-
"""
Created on Thu May 17 14:43:27 2018

@author: Administrator
"""
import os
import urllib3
import random
from urllib3.exceptions import NewConnectionError, ConnectTimeoutError, MaxRetryError,HTTPError,RequestError,ReadTimeoutError,ResponseError

   
try:
    with open('user-agents.txt') as f:
       lines = f.read().splitlines()
    agent=random.choice(lines)
    proxy = urllib3.ProxyManager('http://182.106.140.122:80/',headers={'user-agent': 'Mozilla/5.0 (Darwin; FreeBSD 5.6; en-GB; rv:1.9.1b3pre)Gecko/20081211 K-Meleon/1.5.2'})
    r=proxy.request('GET',  'http://quotes.money.163.com/service/zycwzb_002243.html?part=yynl', preload_content=False, retries=2,
                              timeout=urllib3.Timeout(connect=45, read=240))
    basedir=os.path.dirname(os.path.realpath(__file__))
    filename =os.path.join( basedir,"data" , '002243.csv')
    with open(filename , "wb") as code:     
        code.write(r.data) 
except (NewConnectionError, ConnectTimeoutError, MaxRetryError,HTTPError,RequestError,ReadTimeoutError,ResponseError) as error:
    print('Data   download failed because : %s'%   str(error) )
finally:
    pass       