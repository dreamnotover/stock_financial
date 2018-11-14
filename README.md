
# stock_financial
爬取网易A股财报数据，并使用不断更换代理ip的方式绕过百度反爬虫策略。
由于抓取财报数据一定要完整抓取，在抓取失败后不断更换代理抓取。
次爬虫还需要优化的部分是：当抓取的代理数目减少到一定数量时应该重新抓取代理，没时间优化，实践中直接改写stock——list
主要程序163_data_download.py
抓取代理程序ip_pool.py，与参考程序不一样之处在于使用了chrome driver，注意执行文件地址D:\\chromedriver.exe，此文件需要
下载，因为好多代理网站用urllib、request取不到内容。
网易财报的的规则部分参考了另外一个源，但git地址找不到了，只能抱歉了。
网易财报导入可通过读取文本文件后，将dataframe转置再插入，原来看到的源那一部分写得不好，但目前没时间改进，就先不做了。如果对您能有点帮助，请star。

链接: https://pan.baidu.com/s/1zUaA4Q_sHs2lsI3Nb1_v0g 密码: c5xv

def get_proxy_list2(self,url,url_xpath):
        '''
        返回抓取到代理的列表
        整个爬虫的关键
        '''
        options = webdriver.ChromeOptions()  
   
        options.add_argument("--headless")  
        browser = webdriver.Chrome(chrome_options = options,executable_path='D:\\chromedriver.exe')
        browser.implicitly_wait(30)
        browser.maximize_window()
        proxy_list = []
        
        browser.get(url)
        browser.implicitly_wait(3)
        # 找到代理table的位置
        elements = browser.find_elements_by_xpath(url_xpath)
        for element in elements:           
            ip = element.find_element_by_xpath('./td[1]').text
            port = element.find_element_by_xpath('./td[2]').text
            ip_addr=ip+':' +port
            print( ip_addr)
            proxy_list.append( ip_addr)
                
        browser.quit()
        return proxy_list
参考资料： https://github.com/fancoo/BaiduCrawler/
