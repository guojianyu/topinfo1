import grequests
import grequests
import time
import requests
urls = [
    'https://docs.python.org/2.7/library/index.html',
    'https://docs.python.org/2.7/library/dl.html',
    'http://www.iciba.com/partial',
    'http://2489843.blog.51cto.com/2479843/1407808',
    'http://blog.csdn.net/woshiaotian/article/details/61027814',
    'https://docs.python.org/2.7/library/unix.html',
    'http://2489843.blog.51cto.com/2479843/1386820',
    'http://www.bazhuayu.com/tutorial/extract_loop_url.aspx?t=0',
]


def method3():
    headersParameters = {  # 发送HTTP请求时的HEAD信息，用于伪装为浏览器
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    tasks = [grequests.get(u, headers=headersParameters) for u in urls]
    t1 = time.time()
    res = grequests.map(tasks, size=6,gtimeout=30)
    print (res,len(res))
#   print res
    t2 = time.time()
    print('method3', t2 - t1)
if __name__ == '__main__':
    method3()