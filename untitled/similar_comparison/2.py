import pymssql,datetime,random
import requests
import re,time
from bs4 import BeautifulSoup
from lxml import etree
import jieba_cut
import DB_Connect
from  newspaper import  Article
from multiprocessing import Process
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
        'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    text = Article(url='', language='zh', headers=headersParameters, timeout=req_timeout)
    test = requests.get(url, headers=headersParameters, timeout=req_timeout)
    start = time.time()
    text.download(input_html=test.text)
    # print('download 用时：',time.time()-start)
    start = time.time()
    text.parse()
    # print ('parse 用时:',time.time()-start)
    return test.url,text

def  find_max_similar(data_col,db_obj):#找到最大相似度
    headersParameters = {  # 发送HTTP请求时的HEAD信息，用于伪装为浏览器
        'Connection': 'Keep-Alive',
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    for data in data_col:
        try:
            print (data)
            max_simil = 0 # 用户与记录最大相似度
            max_simil_url = ''
            content_url = ''
            summary_url=''
            ciping_url = ''
            meta_description = ''
            meta_keywords=''
            meta_title=''
            rid = data[0]  # 文章的id
            title = data[1]  # 文章的标题1
            title = re.sub('-','_',re.sub('\(.*?\)','',title)).split('_')
            if len(title[0]) < 5:
                title = "".join(title)
            else:
                title = title[0]
            content = data[2]  # 文章的内容15
            content = filter_tags(content)
            #print('title:', title)
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
                        parse_article_summary += tmp1.group(0)
            except:  # 没有网页内容
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
                    if max_simil <= similarity:
                        ciping_url = res2
                        summary_url = summary[j].xpath('string(.)')  # 获取百度搜索的摘要
                        max_simil_url =res_url
                        max_simil = similarity
                        content_url = content_txt.text
                        meta_description = content_txt.meta_description
                        meta_keywords = content_txt.meta_keywords
                        meta_title = content_txt.title
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
                            if max_simil <= similarity:
                                ciping_url = res2
                                summary_url = summary[j].xpath('string(.)')# 获取百度搜索的摘要
                                max_simil_url =  res_url
                                max_simil = similarity
                                content_url = content_txt.text
                                meta_description = content_txt.meta_description
                                meta_keywords = content_txt.meta_keywords
                                meta_title = content_txt.title
                        except Exception as e:
                            continue
                except:
                    break
            """
            print('百度摘要：',summary_url)
            print('文章内容：',content_url)

            print ('文章meta_descriptio：',meta_description)
            print('最大相似度：', max_simil)
            print('最大相似度url', max_simil_url)
            print('文章id:', rid)
            print('文章标题：', title)
            """
            # 记录到表
            try:
                #db_obj.update_Article_List_Summary(parse_article_summary,rid)
                article_summary = ''
                try:
                    for item in range(6):
                        tmp = re.search('.{0,25}%s.{0,25}' % ciping_url[item][0], content_url.strip(), re.DOTALL)  # 从文章截取标题
                        if tmp:
                            article_summary += tmp.group(0)
                except:#没有网页内容
                    pass
                tmp_ci = ''
                for ci in ciping_url:
                    tmp_ci = "".join([tmp_ci, ci[0], ":", str(round(ci[1], 2)), '|'])
                #print ('meta:',meta_title,'meta1++',type(meta_keywords))
                db_obj.insert_Compare_List(rid,max_simil_url,summary_url,meta_description,content_url,article_summary, tmp_ci,round( max_simil, 2),meta_title,",".join(meta_keywords))
                #将文章和从搜索引擎搜索出来的最大相似文章记录
                db_obj.update_compare_flag(rid)#文章数据库标识得到结果
                for related_txt in related_search: # 将相关搜索词条插入数据库
                    db_obj.insert_Compare_Related(rid, related_txt)
            except Exception as e:
                print (e)
                print('3:出错id:',rid,'标题：',meta_title,'描述：',meta_description,'关键字：',meta_keywords)
        except Exception as e:
            print ('4:',e)
class task_opt():
    def __init__(self):
        DB_DICT = {
            #'server': '192.168.1.189',
            'server': '192.168.0.9',
            'user': 'sa',
            'password': 'Q!W@E#R$T%2015q1w2e3r4t5',
            #'database': 'TOPTHEALTH2017'
            'database': 'DBS_Crawl_02'
        }
        self.db_obj =SqlRW(**DB_DICT)#实例化数据库对象

    def insert_Compare_Related(self,Article_RID,Related_Txt):#将相关搜索插入数据库
        sql = "insert into Compare_Related(Article_RID,Related_Txt) VALUES (% r,%r);" % (
            Article_RID,Related_Txt)
        self.db_obj.WriteSql(sql)
    def insert_Compare_List(self,Article_RID,Baidu_URL,Compare_Summary_Baidu,Compare_Description,Compare_Content,Compare_Summary,Compare_Note,Compare_Rate,Compare_Title,Compare_Keywords):#文章临时表
        print ('Baidu_URL:',Baidu_URL)
        print ('Compare_Summary_Baidu:',Compare_Summary_Baidu)
        print ('Compare_Description:',Compare_Description)
        print ('Compare_Content:',Compare_Content)
        print ('Compare_Summary:',Compare_Summary)
        print ('Compare_Note:',Compare_Note)
        print ('Compare_Rate:',Compare_Rate)
        print ('Compare_Title:',Compare_Title)
        print('Compare_Keywords:',Compare_Keywords)
        # , Compare_Rate
        Compare_Content= Compare_Content.replace('\u0000', '').replace('\x00', '').replace('"','').replace("'", '').replace('“','').replace('”',"").replace('&quot','')
        with open('test1.txt', 'w') as f:
            f.write(Compare_Content)
        #sql = "insert into Compare_List(Article_RID,Compare_URL,Compare_Title,Compare_Keywords,Compare_Summary_Baidu,Compare_Description,Compare_Content,Compare_Summary,Compare_Note,Compare_Rate) VALUES (%r,%r,%r,%r,%r,%r,%r,%r,%r,%r);" % (
            #Article_RID, Baidu_URL,Compare_Title ,Compare_Keywords, Compare_Summary_Baidu,Compare_Description.replace, Compare_Content, Compare_Summary,Compare_Note,Compare_Rate)
        """
        sql = "insert into Compare_List(Article_RID,Compare_URL,Compare_Title,Compare_Keywords,Compare_Summary_Baidu,Compare_Description,Compare_Content) VALUES (%r,%r,%r,%r,%r,%r,%r);" % (
            Article_RID, Baidu_URL, Compare_Title.replace('\u0000', '').replace('\x00', '').replace("'", "").replace('"','').replace("'", '').replace('“','').replace('”',""), Compare_Keywords.replace('\u0000', '').replace('\x00', '').replace("'", "").replace('"','').replace("'", '').replace('“','').replace('”',""),
            Compare_Summary_Baidu.replace('\u0000', '').replace('\x00', '').replace("'", "").replace('"','').replace("'", '').replace('“','').replace('”',""), Compare_Description.replace('\u0000', '').replace('\x00', '').replace("'", "").replace('"','').replace("'", '').replace('“','').replace('”',""),
            '"'+Compare_Content.replace('\u0000', '').replace('\x00', '').replace('"','').replace("'", '').replace('“','').replace('”',"").replace('&quot','')+'"')
        """
        sql = 'insert into Compare_List(Compare_Content) VALUES (%r);'%(Compare_Content[0:1843].replace('\u0000', '').replace('\x00', '').replace('"','').replace("'", "\'").replace('“','').replace('”',"").replace('&quot',''))
        print (sql)
        self.db_obj.WriteSql(sql)
        #self.db_obj.newWriteSql(sql,par)
    def insert_Article_Tags(self,art_id,tag,rate):#添加名词词频和频率
        sql = "insert into Article_Tags(Article_RID,Article_tag,Article_Rate) VALUES (% r,%r,%r);" % (
        art_id, tag, rate)
        self.db_obj.WriteSql(sql)
    def select_Article_List(self):#自身比较
        Sql_info = "select top 600 RID,Article_Title,Article_Content from Article_list WHERE (isNote=0);" #根据任务ID得到具体任务信息
        result = self.db_obj.ReadSql(Sql_info)
        return result
    def select_compare_Article_List(self):
        Sql_info = "select top 600 RID,Article_Title,Article_Content from Article_list WHERE (isCompare=0);"  # 根据任务ID得到具体任务信息
        result = self.db_obj.ReadSql(Sql_info)
        return result
    def update_compare_flag(self,id,flag='1'):
        sql = "update Article_list set isCompare= %r  WHERE RID=%r;" % (flag, id)
        print(sql)
        self.db_obj.WriteSql(sql)
    def update_Article_List(self,id,note):
        sql = "update Article_list set Article_Note= %r,isNote= 1 WHERE RID=%r;" % (note,id)
        self.db_obj.WriteSql(sql)
    def select_Compare_List(self):#得到获取过文章最大相似度的文章id
        Sql_info = "select * from Compare_List;"  # 根据任务ID得到具体任务信息
        result = self.db_obj.ReadSql(Sql_info)
        return result
    def update_Article_List_Summary(self,summary,id):
        sql = "update Article_list set Article_Summary= %r WHERE RID=%r;" % (summary, id)
        self.db_obj.WriteSql(sql)
    def look_biao(self):
        Sql_info = "select  RID,Article_Title,Article_Content from Article_list WHERE RID=687103;"  # 根据任务ID得到具体任务信息
        result = self.db_obj.ReadSql(Sql_info)
        return result
class SqlRW(object):
    def __init__(self, server, user, password, database):
        self.server = server
        self.user = user
        self.password = password
        self.database = database

    def __GetConnect(self):
        self.conn = pymssql.connect(self.server, self.user, self.password, self.database,charset='utf8')
        cursor = self.conn.cursor()
        if not cursor:
            print ('connected failed')
        return cursor


    def ReadSql(self,sql):
        cursor = self.__GetConnect()
        cursor.execute(sql)
        result = cursor.fetchall()
        self.conn.close()
        return result

    def WriteSql(self, sql):
        cursor = self.__GetConnect()
        cursor.execute(sql)
        self.conn.commit()
        self.conn.close()
        return 1
    def newWriteSql(self,sql,par):
        cursor = self.__GetConnect()
        cursor.execute(sql,par)
        self.conn.commit()
        self.conn.close()
        return 1
if __name__ == "__main__":
    import time
    t = task_opt()
  #  肝脏:0.23 | 护肝:0.07 | 肝炎:0.06 | 酒精:0.05 | 维生素:0.05 | 肝细胞:0.05 | 食物:0.05 | 解毒:0.05 | 作用:0.04 | 肝病:0.04 | 可以:0.04 | 修复:0.03 | 解酒:0.03 | 蛋白质:0.03 | 功效:0.03 | 养肝护:0.03 | 养肝:0.03 | 功能:0.03 | 代谢:0.03 | 药物:0.03 | ',)
    #t.delt_crawl_info()
    dat=t.look_biao()
    find_max_similar(dat,t)

    """
    start_time = time.time()
    start_len = len(t.look_biao())
    while True:
        if time.time()-start_time >=60:
            start_time = time.time()
            end_len = len(t.look_biao())
            print ('1分钟比对个数：',end_len-start_len)
            start_len = end_len
    """







