# -*- coding:utf-8 -*-

from urllib import request
# =============================================================================
# 
# with request.urlopen('http://www.baidu.com') as f:
#     data = f.read()
# # 打印状态码看是否成功
#     print('status:',f.status,f.reason)
#     for k,v in f.getheaders():
#         print('%s:%s' % (k,v))
#     print('data:',data.decode('utf-8'))
#  
# =============================================================================

# 创建request对象
req = request.Request('http://www.douban.com/')
# 添加请求头
req.add_header('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0       like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
with request.urlopen(req) as f:
    data = f.read()
    # 打印状态码看是否成功
    print('status:',f.status,f.reason)
    for k,v in f.getheaders():
        print('%s:%s' % (k,v))
    print('data:',data.decode('utf-8'))
def download_stock_data(csv_url):

    response = request.urlopen(csv_url)

    csv = response.read()

    csv_str = str(csv)
    csv_str= csv_str.encode().decode('utf-8')

    lines = csv_str.split("\\n")

    dest_url = r'163.csv'

    fx = open(dest_url, "w")

    for line in lines:

        fx.write(line + "\n")

    fx.close()



download_stock_data('http://quotes.money.163.com/service/zycwzb_300608.html?part=yynl')