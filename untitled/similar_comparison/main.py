#从文章链表获取一条文章并从搜索引擎中搜索出最大相似度的文章进行记录
#文章增加一个字段记录是否得到过最大相似度
import requests
import re
from bs4 import BeautifulSoup
from lxml import etree
import jieba_cut
import DB_Connect
from multiprocessing import Process

get_page_count =2#比对前几页的文章
req_timeout = 30#请求url的超时事件

def get_text(url):
    headersParameters = {  # 发送HTTP请求时的HEAD信息，用于伪装为浏览器
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    #input = 'http://blog.sina.com.cn/s/blog_858e4c190102wn4u.html'
    input= url
    test = requests.get(input,headers= headersParameters,timeout=req_timeout)

    soup = BeautifulSoup(test.content, "lxml")
    [script.extract() for script in soup.findAll('script')]
    [style.extract() for style in soup.findAll('style')]
    soup.prettify()
    text = soup.get_text()# 获取页面所有文本内容
    return  test.url,text

def  find_max_similar(data_col,db_obj):#找到最大相似度
    headersParameters = {  # 发送HTTP请求时的HEAD信息，用于伪装为浏览器
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    try:
        for data in data_col:
            max_simil = 0  # 用户与记录最大相似度
            max_simil_url = ''
            rid = data[0]  # 文章的id
            title = data[1]  # 文章的标题1
            title = re.sub('-','_',re.sub('\(.*?\)','',title)).split('_')
            if len(tmp[0]) < 5:
                title = "".join(title)
            else:
                title = title[0]

            content = data[2]  # 文章的内容15
            print('title:', title)
            print('content:', content)
            content = content.replace(r'\n', '')
            tmp_url = 'http://www.baidu.com/s?wd=%s' % '"' + title + '"'  # 进入搜索首页
            test = requests.get(tmp_url, headers=headersParameters, timeout=req_timeout)
            root = etree.HTML(test.content)
            tmp = root.xpath("//h3[@class='t']/a")
            res1 = jieba_cut.cut_word(content)
            for i in tmp:
                try:
                    url = i.get('href')
                    record_url, res2 = get_text(url)  # 请求超时
                except:
                    continue
                res2 = jieba_cut.cut_word(res2)
                vectors = jieba_cut.tf_idf(res1=res1, res2=res2)
                similarity = jieba_cut.run(vector1=vectors[0], vector2=vectors[1])
                #print(url, ':', similarity)
                if max_simil <= similarity:
                    max_simil_url = record_url
                    max_simil = similarity
            for _ in range(1, get_page_count):  # 翻多少页
                try:  # 没有下一页
                    next_page = root.xpath("//div[@id='page']/a[@class='n']/@href")[-1]
                    next_page = 'http://www.baidu.com' + next_page
                    test = requests.get(next_page, headers=headersParameters, timeout=req_timeout)
                    root = etree.HTML(test.content)
                    #print(next_page)
                    tmp = root.xpath("//h3[@class='t']/a")
                    for i in tmp:
                        url = i.get('href')
                        try:
                            record_url, res2 = get_text(url)
                        except:
                            continue
                        res2 = jieba_cut.cut_word(res2)
                        vectors = jieba_cut.tf_idf(res1=res1, res2=res2)
                        similarity = jieba_cut.run(vector1=vectors[0], vector2=vectors[1])
                        #print(url, ':', similarity)
                        if max_simil <= similarity:
                            max_simil_url = record_url
                            max_simil = similarity
                except:
                    break
            """
            print('最大相似度：', max_simil)
            print('最大相似度url', max_simil_url)
            print('文章id:', rid)
            print('文章标题：', title)
            """
            # 记录到表
            try:
                db_obj.insert_Compare_List(rid,max_simil_url, max_simil)#将文章和从搜索引擎搜索出来的最大相似文章记录
                db_obj.update_compare_flag(rid)#文章数据库标识得到结果
            except:
                pass
    except Exception as e:
        print (e)


if __name__ == '__main__':
    print ('start')
    t = DB_Connect.task_opt()
    while True:
        data_col = t.select_compare_Article_List()
        sign_count = len(data_col) // 6#平均分成6份
        yushu = len(data_col) % 6
        end_count = 0
        tmp_list = []
        print('get datalength:>',len(data_col))
        if sign_count ==0:
            find_max_similar(data_col,t)
        else:
            for i in range(6):  # 开启6个进程
                a = data_col[end_count:end_count+ sign_count]
                end_count = end_count + sign_count
                p = Process(target=find_max_similar, args=(a,t))
                tmp_list.append(p)

            tmp_list.append(Process(target=find_max_similar, args=(data_col[end_count:],t)))
            for item in tmp_list:
                item.start()

            for item in tmp_list:
                item.join()
            for item in tmp_list:
                print ('kill+++')
                item.terminate()
