#获取摘要，百度摘要和文章内部的摘要
import jieba.analyse
import requests
from  newspaper import  Article
import time
from fake_useragent import UserAgent
ua = UserAgent()
from newspaper import fulltext
url = 'https://www.baidu.com/link?url=gy46y9WcUxfkKFJecnoPLs72zaRJfTfDY8EAMxLiuk_7qGuvp5J3Hcc-S9U50eIdTpoTfToAQu8P1YwXRByfp_Z5zcD55XMEfLaPhgNNTz3&wd=&eqid=cea622c70001db1f000000035a3b0be6'
def extractText(url):
    req_timeout = 30
    headersParameters = {  # 发送HTTP请求时的HEAD信息，用于伪装为浏览器
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent':ua.random
    }
    a = Article(url, language='zh', keep_article_html=True,headers=headersParameters)
    a.download()
    a.parse()
    return a
url = 'https://www.baidu.com/search/error.html'
#url = 'https://www.cnblogs.com/yfceshi/p/6985167.html'
#a = extractText(url)
#print (a.text)
def cut_word(article):
    # 这里使用了TF-IDF算法，所以分词结果会有些不同->https://github.com/fxsjy/jieba#3-关键词提取
    res = jieba.analyse.extract_tags(
        sentence=article, topK=20, withWeight=True,allowPOS=('n'))
    return res
#res = cut_word(a.text)
#print (res)
headersParameters = {  # 发送HTTP请求时的HEAD信息，用于伪装为浏览器
    'Connection': 'Keep-Alive',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent': 'Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'
}
url = 'https://www.baidu.com/'
start = time.time()
text = requests.get(url,headers=headersParameters)
print (text.text)
"""
a = Article(url='', language='zh', keep_article_html=True,headers=headersParameters)
a.download(input_html=text.text)
print (a.download_state)
a.parse()
print (time.time()-start,'结束时间')
print(a.text)
print (a.title)
print (a.meta_description)
print (str(a.meta_keywords))
"""

