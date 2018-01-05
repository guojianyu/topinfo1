import requests
import re,time
from bs4 import BeautifulSoup
from lxml import etree
import jieba_cut
import DB_Connect
from  newspaper import  Article
from multiprocessing import Process
from fake_useragent import UserAgent
ua = UserAgent()
get_page_count =1#比对前几页的文章
req_timeout = 30#请求url的超时事件
def filter_tags(htmlstr):
    #先过滤CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?\w+[^>]*>')#HTML标签
    re_comment=re.compile('<!--[^>]*-->')#HTML注释
    s=re_script.sub('',htmlstr) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    return s

def get_text(url):
    headersParameters = {  # 发送HTTP请求时的HEAD信息，用于伪装为浏览器
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': ua.random
    }
    text = Article(url='', language='zh', headers=headersParameters, timeout=req_timeout)
    test = requests.get(url, headers=headersParameters, timeout=req_timeout)
    if test.encoding == 'UTF-8':
        html = test.text
    elif test.encoding == 'ISO-8859-1':
        try:
            html = test.text.encode('ISO-8859-1').decode('gbk').encode('utf-8').decode('utf-8')
        except:
            html = test.text.encode('ISO-8859-1').decode('utf-8')
    else:
        html = test.text
    text.download(input_html=html)
    text.parse()
    # print ('parse 用时:',time.time()-start)
    return test.url,text

def  find_max_similar(data_col,db_obj):#找到最大相似度
    headersParameters = {  # 发送HTTP请求时的HEAD信息，用于伪装为浏览器
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent':ua.random
    }
    for data in data_col:
        try:
            rid = data[0]  # 文章的id
            title = data[1]  # 文章的标题1
            title = re.sub('-','_',re.sub('\(.*?\)','',title)).split('_')
            if len(title[0]) < 5:
                title = "".join(title)
            else:
                title = title[0]
            content = data[2]  # 文章的内容15
            content = filter_tags(content)
           # print('title:', title)
            content = content.replace(r'\n', '')
            #print('content:', content)
            tmp_url = 'http://www.baidu.com/s?wd=%s' % '"' + title + '"'  # 进入搜索首页
            test = requests.get(tmp_url, headers=headersParameters, timeout=req_timeout)
            root = etree.HTML(test.content)
            tmp = root.xpath("//h3[@class='t']/a")
            if len(tmp)<=0:
                db_obj.update_compare_flag(rid,'2')#百度搜索框没右结果
                continue
            summary = root.xpath("//div[@class='c-abstract']|//div[@class='c-abstract c-abstract-en']")
            res1 = jieba_cut.cut_word(content)
            parse_article_summary = ''
            try:
                for item in range(6):
                    tmp1 = re.search('.{0,25}%s.{0,25}' % res1[item][0], content.strip(), re.DOTALL)  # 从文章截取标题
                    if tmp1:
                        parse_article_summary = "...".join([parse_article_summary,tmp1.group(0)])
            except:  # 没有网页内容
                pass
            try:
                db_obj.insert_Article_List_Summary(parse_article_summary, rid)
            except:
                pass
            #获取相关搜索
            related_search = root.xpath("//div[@id='rs']/table/tr/th/a/text()")
            for j,i in enumerate(tmp):
                try:
                    url = i.get('href')
                    res_url,content_txt = get_text(url)  # 请求超时
                    res2 = jieba_cut.cut_word(content_txt.text)
                    vectors = jieba_cut.tf_idf(res1=res1, res2=res2)
                    similarity = jieba_cut.run(vector1=vectors[0], vector2=vectors[1])
                    # print(url, ':', similarity)
                    ciping_url = res2
                    summary_url = summary[j].xpath('string(.)')  # 获取百度搜索的摘要
                    max_simil_url =res_url
                    max_simil = similarity
                    content_url = content_txt.text
                    meta_description = content_txt.meta_description
                    meta_keywords = content_txt.meta_keywords
                    meta_title = content_txt.title
                    try:
                        article_summary = ''
                        try:
                            for item in range(6):
                                tmp = re.search('.{0,25}%s.{0,25}' % ciping_url[item][0], content_url.strip(),
                                                re.DOTALL)  # 从文章截取标题
                                if tmp:
                                    article_summary = "...".join([article_summary,  tmp.group(0)])
                        except:  # 没有网页内容
                            pass
                        tmp_ci = ''
                        for ci in ciping_url:
                            tmp_ci = "".join([tmp_ci, ci[0], ":", str(round(ci[1], 2)), '|'])
                        db_obj.insert_Compare_List(rid, max_simil_url, summary_url, meta_description, content_url,
                                                   article_summary, tmp_ci, round(max_simil, 2), meta_title,
                                                   ",".join(meta_keywords))
                        # 将文章和从搜索引擎搜索出来的最大相似文章记录
                        db_obj.update_compare_flag(rid)  # 文章数据库标识得到结果
                        for related_txt in related_search:  # 将相关搜索词条插入数据库
                            db_obj.insert_Compare_Related(rid, related_txt)
                    except Exception as e:
                        print(e)
                        print('3:出错id:', rid, '标题：', meta_title, '描述：', meta_description, '关键字：', meta_keywords)
                        print('文章摘要：', parse_article_summary)
                except Exception as e:
                    continue

            for _ in range(1, get_page_count):  # 翻多少页
                try:  # 没有下一页
                    next_page = root.xpath("//div[@id='page']/a[@class='n']/@href")[-1]
                    next_page = 'http://www.baidu.com' + next_page
                    test = requests.get(next_page, headers=headersParameters, timeout=req_timeout)
                    root = etree.HTML(test.content)
                    #print(next_page)
                    tmp = root.xpath("//h3[@class='t']/a")
                    summary = root.xpath("//div[@class='c-abstract']|//div[@class='c-abstract c-abstract-en']")
                    for j,i in enumerate(tmp):
                        try:
                            url = i.get('href')
                            res_url,content_txt = get_text(url)
                            res2 = jieba_cut.cut_word(content_txt.text)
                            vectors = jieba_cut.tf_idf(res1=res1, res2=res2)
                            similarity = jieba_cut.run(vector1=vectors[0], vector2=vectors[1])
                            ciping_url = res2
                            summary_url = summary[j].xpath('string(.)')# 获取百度搜索的摘要
                            max_simil_url =  res_url
                            max_simil = similarity
                            content_url = content_txt.text
                            meta_description = content_txt.meta_description
                            meta_keywords = content_txt.meta_keywords
                            meta_title = content_txt.title
                            try:
                                article_summary = ''
                                try:
                                    for item in range(6):
                                        tmp = re.search('.{0,25}%s.{0,25}' % ciping_url[item][0],
                                                        content_url.strip(), re.DOTALL)  # 从文章截取标题
                                        if tmp:
                                            article_summary += tmp.group(0)
                                except:  # 没有网页内容
                                    pass
                                tmp_ci = ''
                                for ci in ciping_url:
                                    tmp_ci = "".join([tmp_ci, ci[0], ":", str(round(ci[1], 2)), '|'])
                                # print ('meta:',meta_title,'meta1++',type(meta_keywords))
                                db_obj.insert_Compare_List(rid, max_simil_url, summary_url, meta_description,
                                                           content_url, article_summary, tmp_ci,
                                                           round(max_simil, 2), meta_title, ",".join(meta_keywords))
                                # 将文章和从搜索引擎搜索出来的最大相似文章记录
                                db_obj.update_compare_flag(rid)  # 文章数据库标识得到结果
                                for related_txt in related_search:  # 将相关搜索词条插入数据库
                                    db_obj.insert_Compare_Related(rid, related_txt)
                            except Exception as e:
                                print(e)
                                print('3:出错id:', rid, '标题：', meta_title, '描述：', meta_description, '关键字：',
                                      meta_keywords)
                                print('文章摘要：', parse_article_summary)
                        except Exception as e:
                            continue
                except:
                    break
            """
            print('百度摘要：',summary_url)
            print('文章内容：',content_url)
            print('文章内容摘要：', article_summary)
            print ('文章meta_descriptio：',meta_description)
            print('百度词频：',ciping_url)
            print('最大相似度：', max_simil)
            print('最大相似度url', max_simil_url)
            print('文章id:', rid)
            print('文章标题：', title)
            """
            # 记录到表

        except Exception as e:
            print ('4:',e)
if __name__ == '__main__':

    t = DB_Connect.task_opt()
    while True:
        data_col = t.select_compare_Article_List()
        sign_count = len(data_col) // 6  # 平均分成6份
        yushu = len(data_col) % 6
        end_count = 0
        tmp_list = []
        print('get datalength:>', len(data_col))
        if sign_count == 0:
            find_max_similar(data_col, t)
        else:
            for i in range(6):  # 开启6个进程
                a = data_col[end_count:end_count + sign_count]
                end_count = end_count + sign_count
                p = Process(target=find_max_similar, args=(a, t))
                tmp_list.append(p)

            tmp_list.append(Process(target=find_max_similar, args=(data_col[end_count:], t)))
            for item in tmp_list:
                item.start()

            for item in tmp_list:
                item.join()
            for item in tmp_list:
                print('kill+++')
                item.terminate()
    """
    import time
    t = DB_Connect.task_opt()
    a = t.select_compare_Article_List()[0:1000]
    find_max_similar(a,t)
    """
