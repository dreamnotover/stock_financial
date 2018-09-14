# encoding: utf-8
import shutil

__author__ = 'wenhua'
import os
import csv
import re
import sys
import time

from urllib3.exceptions import NewConnectionError, ConnectTimeoutError, MaxRetryError,HTTPError,RequestError,ReadTimeoutError,ResponseError
 
from tools import get_stock_list,insert_query,get_fin_item
import logging
import  datetime
import  json
import random
import urllib3
import random
import config as cfg
import inspect

# set up logging to file - see previous section for more details
basedir=os.path.dirname(os.path.realpath(__file__))
print  ("  base_dir:" +basedir)
logfile="%s\\log\\st_%s.log" %(basedir,datetime.datetime.now().strftime("%Y-%m-%d"))   
logging.basicConfig(filename=logfile, level=logging.DEBUG,format='%(asctime)s %(filename)s:%(lineno)s- %(funcName) %(message)s')
isremovecsv = False  # 是否删掉CSV文件
reporttype = {'利润表': {'url': 'http://quotes.money.163.com/service/lrb_%s.html'},
              '主要财务指标': {'url': 'http://quotes.money.163.com/service/zycwzb_%s.html'},
              '资产负债表': {'url': 'http://quotes.money.163.com/service/zcfzb_%s.html'},
              '财务报表摘要': {'url': 'http://quotes.money.163.com/service/cwbbzy_%s.html'},
              '盈利能力': {'url': 'http://quotes.money.163.com/service/zycwzb_%s.html?part=ylnl'},
              '偿还能力': {'url': 'http://quotes.money.163.com/service/zycwzb_%s.html?part=chnl'},
              '成长能力': {'url': 'http://quotes.money.163.com/service/zycwzb_%s.html?part=cznl'},
              '营运能力': {'url': 'http://quotes.money.163.com/service/zycwzb_%s.html?part=yynl'},
              '现金流量表': {'url': 'http://quotes.money.163.com/service/xjllb_%s.html'}}

itemtype = {}  # 类目
reportlist = []
rows=0
values=[]
useful_proxies={}
conn = pymysql.connect(host='127.0.0.1',  user='root', passwd='root',
                       db='investment',
                       charset='utf8')  # 数据库连接
cur = conn.cursor()

insert_sql = 'INSERT INTO t_163_data (symbol, report_date, item_key, item_value) VALUES (%s, %s, %s, %s)on duplicate key update item_value=values(item_value)'
 

def get_cur_info():
     print('%s -- %s -- %s'%(sys._getframe().f_code.co_filename ,sys._getframe(2).f_code.co_name, sys._getframe().f_lineno))

def lineno():
    """Returns the current line number in our program."""
    return str( inspect.currentframe().f_back.f_lineno)
global  proxy,agent,lines 
 
def get_proxies( ):
    ip_list = []

    # 连接数据库
    conn = pymysql.connect(cfg.host, cfg.user, cfg.passwd, cfg.DB_NAME)
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

def delete_proxy (prox_address ):
    if(len(prox_address)>11):
        # 连接数据库
        conn = pymysql.connect(cfg.host, cfg.user, cfg.passwd, cfg.DB_NAME)
        cursor = conn.cursor()
        addr=prox_address[7:]
        # 检查数据表中是否有数据
        try:
            sql="delete  FROM  valid_ip where content= '%s'" % addr
            cursor.execute(sql)
              
        except Exception as e:
            print ("从数据库删除ip失败！")
        finally:
            cursor.close()
            conn.close()
    
        

def download(symbol, reportname,u_proxy,proxy, retries=3):
    # 下载文件
    global useful_proxies
    try:
        response=u_proxy.request('GET',  reporttype[reportname]['url'] % symbol, preload_content=False,
                          timeout=urllib3.Timeout(connect=45, read=100))              
        if response.status==200:
           # print(content)
            filename =os.path.join( basedir,"csv" , symbol, reportname + '.csv') 
            profitfile = open(filename, 'wb+')            
            profitfile.write(response.data)
            profitfile.close()
            itemtype= get_fin_item(reportname)
            import_report(reportname,itemtype,filename)
            print(symbol+" " +reportname+"  download and  import succeeded!")
            logging.info(lineno()+" " +symbol+" " +reportname+"  download and  import succeeded!")
            print('%s -- %s -- %s'%(sys._getframe().f_code.co_filename ,sys._getframe(2).f_code.co_name, sys._getframe().f_lineno))
            return  True
        else:
            print(symbol+" " +reportname+"  download failed!")
            logging.info(symbol+" " +reportname+"  download failed!")
            if retries == 0:    
                agent=random.choice(lines)
                proxy = random.choice(list(useful_proxies))
                print(lineno()+" " + "change proxies: " + proxy)
                logging.info( "change proxies: " + proxy)
                u_proxy = urllib3.ProxyManager('http://'+proxy,headers={'user-agent': agent})
                download(symbol, reportname,u_proxy,proxy, retries= 3)
                get_cur_info()
            else:
                download(symbol, reportname,u_proxy,proxy, retries= retries - 1)
            return False
    except (NewConnectionError, ConnectTimeoutError, MaxRetryError,HTTPError,RequestError,ReadTimeoutError,ResponseError) as error:
        logging.error('Data of ' +symbol + 'download failed because' + str(error)) 
        print('Data of %s  %s download failed because %s\nURL: %s'%( symbol,reportname,str(error), reporttype[reportname]['url']%symbol))
       
        if retries > 0:
             print('%s -- %s -- %s'%(sys._getframe().f_code.co_filename ,sys._getframe(2).f_code.co_name, sys._getframe().f_lineno))
             time.sleep( 200 )
             if proxy  in useful_proxies: 
                 useful_proxies[proxy] += 1
                 if useful_proxies[proxy] > 2:
                    del useful_proxies[proxy] 
                    # 再抓一次
                    agent=random.choice(lines)
                    proxy = random.choice(list(useful_proxies))
                    print( "change proxies: " + proxy)
                    logging.info( "change proxies: " + proxy)
                    u_proxy = urllib3.ProxyManager('http://'+proxy,headers={'user-agent': agent})
                    download(symbol, reportname,u_proxy,proxy, 3)
             else:
                download(symbol, reportname,u_proxy,proxy,retries= retries - 1)
        elif retries == 0:
            print('%s -- %s -- %s'%(sys._getframe().f_code.co_filename ,sys._getframe(2).f_code.co_name, sys._getframe().f_lineno))
            if proxy  in useful_proxies: 
                del useful_proxies[proxy]
            delete_proxy (proxy )
            agent=random.choice(lines)
            proxy = random.choice(list(useful_proxies))
            print(lineno()+" " + "change proxies: " + proxy)
            logging.info( "change proxies: " + proxy)
            print('%s -- %s -- %s'%(sys._getframe().f_code.co_filename ,sys._getframe(2).f_code.co_name, sys._getframe().f_lineno))
            u_proxy = urllib3.ProxyManager('http://'+proxy,headers={'user-agent': agent})
            logging.info("Fetch %s report  failed!"% reporttype[reportname]['url']%symbol) 
            download(symbol, reportname,u_proxy,proxy, 3)
            return  True   
        
        else:
           print('%s -- %s -- %s'%(sys._getframe().f_code.co_filename ,sys._getframe(2).f_code.co_name, sys._getframe().f_lineno))
           logging.info("Fetch %s report  failed!"% reporttype[reportname]['url']%symbol)
           return  False
        
    else:
        print('%s -- %s -- %s'%(sys._getframe().f_code.co_filename ,sys._getframe(2).f_code.co_name, sys._getframe().f_lineno))
        useful_proxies[proxy] += 1
        if useful_proxies[proxy] > 2:
           if proxy  in useful_proxies: 
                del useful_proxies[proxy]
           delete_proxy (proxy )
            # 再抓一次
        if retries == 0: 
            print('%s -- %s -- %s'%(sys._getframe().f_code.co_filename ,sys._getframe(2).f_code.co_name, sys._getframe().f_lineno))
            agent=random.choice(lines)
            proxy = random.choice(list(useful_proxies))
            print(lineno()+" " + "change proxies: " + proxy)
            logging.info( "change proxies: " + proxy)
            print('%s -- %s -- %s'%(sys._getframe().f_code.co_filename ,sys._getframe(2).f_code.co_name, sys._getframe().f_lineno))
            u_proxy = urllib3.ProxyManager('http://'+proxy,headers={'user-agent': agent})
            download(symbol, reportname,u_proxy,proxy,  3)
        else:
             print('%s -- %s -- %s'%(sys._getframe().f_code.co_filename ,sys._getframe(2).f_code.co_name, sys._getframe().f_lineno))
             download(symbol, reportname,u_proxy,proxy,retries= retries - 1)
        logging.info("Fetch %s report  failed!"% reporttype[reportname]['url']%symbol)
        print('%s -- %s -- %s'%(sys._getframe().f_code.co_filename ,sys._getframe(2).f_code.co_name, sys._getframe().f_lineno))
        return False
       
    finally:
        pass
   

def import_report(reportname,itemtype,filename):
    global rows
    global values
    # 类目载入
    
    # 读取 csv
    try:
        csvreader = csv.reader(open(filename, 'r', encoding='gbk'))
        for row in csvreader:
            for index, value in enumerate(row):
                if value.strip() == '':
                    continue
                if row[0].strip() == '报告日期' or row[0].strip() == '报告期':
                    if index != 0:
                        profit = {'date': value}  # 创建并加入到列表中
                        reportlist.append(profit)
                else:
                    if index != 0 and index <= len(reportlist):
                        try:
                            value = float(value)
                        except ValueError:
                            value = 0
                        reportlist[index - 1][str(itemtype[row[0].strip()])] = str(value)
    
        # 存库
        for report in reportlist:
            for item in report:
                if item != 'date':
                    
                    sql_data= [ symbol ,  report['date'], item , report[item]]
                    values.append(sql_data)
                    rows=rows+1
                    if (rows % 100 == 0):            
                        insert_query(insert_sql,values)
                        values=[]
        print(symbol + '导入' + reportname + '数据:' + str(len(reportlist)))
        logging.info(symbol + '导入' + reportname + '数据:' + str(len(reportlist)))
        itemtype.clear()
        reportlist.clear()
        pass
    except  Exception as e:
        logging.info("Exeception occured:{}".format(e))
    
# =============================================================================
# reportname='现金流量表'    
# itemtype= get_fin_item(reportname)
# symbol= "600081"
# filename = 'csv/' + symbol + '/' + reportname + '.csv'
# import_report(reportname,itemtype,filename)
# exit()
# =============================================================================
stocklist=get_stock_list()#取得股票列表"300113", "300114", "300115", "300116", "300117", "300118", "300119", "300120", "300121", "300122", "300123", "300124", "300125", "300126", "300127", "300128", "300129", "300130", "300131", "300132", "300133", "300134", "300135", "300136", "300137", "300138", "300139", "300140", "300141", "300142", "300143", "300144", "300145", "300146", "300147", "300148", "300149", "300150", "300151", "300152", "300153","300154", "300155", "300156", "300157", "300158", "300159", "300160", "300161", "300162", "300163", "300164", "300165", "300166", "300167", "300168", "300169", "300170", "300171", "300172", "300173", "300174", "300175", "300176", "300177", "300178", "300179", "300180", "300181", "300182", "300183", "300184", "300185", "300186", "300187", "300188", "300189", "300190", "300191", "300192", "300193", "300194", "300195", "300196", "300197", "300198", "300199", "300200", "300201", "300202", "300203", "300204", "300205", "300206", "300207", "300208", "300209", "300210", "300211", "300212", "300213", "300214", "300215", "300216", "300217", "300218", "300219", "300220", "300221", "300222", "300223", "300224", "300225", "300226", "300227", "300228", "300229", "300230", "300231", "300232", "300233", "300234", "300235", "300236", "300237", "300238", "300239", "300240", "300241", "300242", "300243", "300244", "300245", "300246", "300247", "300248", "300249", "300250", "300251", "300252","300253", "300254", "300255", "300256", "300257", "300258", "300259", "300260", "300261", "300262", "300263", "300264", "300265", "300266", "300267", "300268", "300269", "300270", "300271", "300272", "300273", "300274", "300275", "300276", "300277", "300278", "300279", "300280", "300281", "300282", "300283", "300284", "300285", "300286", "300287", "300288", "300289", "300290", "300291", "300292", "300293", "300294", "300295", "300296", "300297", "300298", "300299", "300300", "300301", "300302", "300303", "300304", "300305", "300306", "300307", "300308", "300309", "300310", "300311", "300312", "300313", "300314", "300315", "300316", "300317", "300318", "300319", "300320", "300321", "300322", "300323", "300324", "300325", "300326", "300327", "300328", "300329", "300330", "300331", "300332", "300333", "300334", "300335", "300336", "300337", "300338", "300339", "300340", "300341", "300342", "300343", "300344", "300345", "300346", "300347", "300348", "300349", "300350", "300351", "300352", "300353", "300354", "300355", "300356", "300357", "300358", "300359", "300360", "300361", "300362", "300363", "300364", "300365", "300366", "300367", "300368", "300369", "300370", "300371", "300372", "300373", "300374", "300375", "300376", "300377", "300378", "300379", "300380", "300381", "300382", "300383", "300384", "300385", "300386", "300387", "300388", "300389", "300390", "300391", "300392", "300393", "300394", "300395", "300396", "300397", "300398", "300399", "300400", "300401", "300402", "300403", "300404", "300405", "300406", "300407", "300408", "300409", "300410", "300411", "300412", "300413", "300414", "300415" , "300416"  "300417", "300418", "300419", "300420", "300421", "300422", "300423", "300424", "300425", "300426", "300427", "300428", "300429", "300430", "300431", "300432", "300433", "300434", "300435", "300436", "300437", "300438", "300439", "300440", "300441", "300442", "300443", "300444", "300445", "300446", "300447", "300448", "300449", "300450", "300451", "300452", "300453", "300454", "300455", "300456", "300457", "300458", "300459", "300460", "300461", "300462", "300463", "300464", "300465", "300466", "300467", "300468", "300469", "300470", "300471", "300472", "300473", "300474", "300475", "300476", "300477", "300478", "300479", "300480", "300481", "300482", "300483", "300484", "300485", "300486", "300487", "300488", "300489", "300490", "300491", "300492", "300493", "300494", "300495", "300496", "300497", "300498", "300499","300327", "300328", "300329", "300330", "300331", "300332", "300333", "300334", "300335", "300336", "300337", "300338", "300339", "300340", "300341", "300342", "300343", "300344", "300345", "300346", "300347", "300348", "300349", "300350", "300351", "300352", "300353", "300354", "300355", "300356", "300357", "300358", "300359", "300360", "300361", "300362", "300363", "300364", "300365", "300366", "300367", "300368", "300369", "300370", "300371", "300372", "300373", "300374", "300375", "300376", "300377", "300378", "300379", "300380", "300381", "300382", "300383", "300384", "300385", "300386", "300387", "300388", "300389", "300390", "300391", "300392", "300393", "300394", "300395", "300396", "300397", "300398", "300399", "300400", "300401", "300402", "300403", "300404", "300405", "300406", "300407", "300408", "300409", "300410", "300411", "300412", "300413", "300414", "300415", "300416","300500", "300501", "300502", "300503", "300504", "300505", "300506", "300507", "300508", "300509", "300510", "300511", "300512", "300513", "300514", "300515", "300516", "300517", "300518", "300519", "300520", "300521", "300522", "300523", "300525", "300526", "300527", "300528", "300529", "300530", "300531", "300532", "300533", "300534", "300535", "300536","300591", "300592", "300593", "300595", "300596", "300597", "300598", "300599", "300609", "300610", "300611", "300612", "300613", "300615", "300616", "300617", "300618", "300619", "300620", "300621", "300622", "300623", "300624", "300625", "300626", "300627", "300628", "300629", "300630", "300631", "300632", "300633", "300634", "300635", "300636", "300637", "300658", "300659", "300660", "300661", "300662", "300663", "300664", "300665", "300666", "300667", "300668", "300669", "300670", "300671", "300672", "300673", "300675", "300676", "300677", "300678", "300679", "300680", "300681", "300682", "300683", "300684", "300700", "300701", "300702", "300703", "300705", "300706", "300707", "300708", "300709", "300710", "300711", "300712", "300713", "300715", "300716", "300717", "300718", "300719", "300720", "300699","300721", "300722", "300723", "300725", "300726", "300727", "300728", "300729", "300730", "300731", "300732", "300733", "300735", "300736", "300737" 
#stocklist=[  "300081", "300082", "300083", "300084", "300085", "300086", "300087", "300088", "300089", "300090", "300091", "300092", "300093", "300094", "300095", "300096", "300097", "300098", "300099", "300100", "300101", "300102", "300103", "300104", "300105", "300106", "300107", "300108", "300109", "300110", "300111", "300112"       ]
#logging.info('stocklist:'+json.JSONEncoder().encode(stocklist))
logging.info('Import stock  finatial begins:')
with open(basedir+'\\user-agents.txt') as f:
   lines = f.read().splitlines()
#stocklist=['600000','000807']
useful_proxies = {}
    
try:
    # 获取代理IP数据
    for ip in get_proxies():
        useful_proxies[ip] = 0
    print( "总共：%s 'IP可用'" %len(useful_proxies))
except OSError:
    print ("获取代理ip时出错！")
processed=1

if len(stocklist) == 0:
    pass
else:
    for symbol in stocklist:
        print('# --------------------------------------------')
        logging.info("download"+symbol+ "begins")
        file_path=os.path.join( basedir,"csv" , symbol)
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        if  processed == 1 or  processed%10==0:    
            agent=random.choice(lines)
            proxy = random.choice(list(useful_proxies))
            print( "change proxies: " + proxy)
            u_proxy = urllib3.ProxyManager('http://'+proxy,headers={'user-agent': agent})
        processed=processed+1    
        for i in reporttype:            
            ret=download(symbol, i,u_proxy, proxy,3)            
            time.sleep( 10 )
    if isremovecsv:
        shutil.rmtree('csv/' + symbol)
#    cur.execute(executesql[:-1])
    
pass
if  len(values) > 0 : 
    insert_query(insert_sql,values)
    values=[]

logging.info("download ended") 
