import requests,re,json,copy,os,time
import DB_Connect
from bs4 import BeautifulSoup
req_timeout = 30#请求url的超时事件
class crawl_obj:
    def __init__(self):
        self.db_obj = DB_Connect.task_opt()#操作数据库对象
    def run(self):
        while True:
            data_coll= self.db_obj.select_test()
            if not len(data_coll):
                time.sleep(1)
                continue
            for data in data_coll:
                print ('获得任务')
                self.get_filter_rule(data)
                all_link = self.get_all_link(input_url=self.input_url,Task_Deep=self.Task_Deep)
                print (len(all_link))
                for i in all_link:
                    for count,item in enumerate(self.Task_Match_rule):
                        tmp = [item[i:i + 2] for i in range(0, len(item), 2)]
                        print ('匹配规则：',tmp)
                        print ('匹配字段',self.Task_Match_field[count])
                        print('url:',i)
                        a = self.test(i,tmp)
                        print ('匹配结果为：',a)
                self.db_obj.update_ready_status(id=data[-1],flag=2)#更新任务状态为2完成状态
    def get_filter_rule(self,data):#得到url过滤条件
        self.domain_list = []  # 存放域名规则的列表
        self.dirct_list = []  # 存放目录规则的列表
        self.file_name = []  # 存放文件名称的规则
        self.domain1_list = []  # 存放域名规则的列表
        self.dirct1_list = []  # 存放目录规则的列表
        self.file1_name = []  # 存放文件名称的规则
        self.input_url = data[0]
        Task_On_rule = json.loads(data[1].replace('\\"','"'))
        Task_Out_rule = json.loads(data[2].replace('\\"','"'))
        self.Task_Deep = int(data[3])
        self.Task_Match_field = json.loads(data[4].replace('\\"','"'))
        self.Task_Match_rule = json.loads(data[5].replace('\\"','"'))
        for item in Task_On_rule:
            tmp = item.split(':')
            if tmp[0] == '0':  # 得到url的过滤分类,域名分类
                self.domain_list.append(":".join(tmp[1:]))
            elif tmp[0] == '1':  # 目录分类
                self.dirct_list.append(":".join(tmp[1:]))
            elif tmp[0] == '2':  # 文件名分类
                self.file_name.append(":".join(tmp[1:]))
        for item in Task_Out_rule:
            tmp = item.split(':')
            if tmp[0] == '0':  # 得到url的过滤分类,域名分类
                self.domain1_list.append(":".join(tmp[1:]))
            elif tmp[0] == '1':  # 目录分类
                self.dirct1_list.append(":".join(tmp[1:]))
            elif tmp[0] == '2':  # 文件名分类
                self.file1_name.append(":".join(tmp[1:]))

    def get_text(self,url):
        html = ''
        headersParameters = {  # 发送HTTP请求时的HEAD信息，用于伪装为浏览器
            'Connection': 'Keep-Alive',
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Language': 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/6.1 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko'
        }
        try:
            test = requests.get(url, headers=headersParameters, timeout=req_timeout)
            if test.encoding == 'ISO-8859-1':
                try:
                    html = test.text.encode('ISO-8859-1').decode('gbk').encode('utf-8').decode('utf-8')
                except:
                    try:
                        html = test.text.encode('ISO-8859-1').decode('utf-8')
                    except:
                        test.encoding = test.apparent_encoding
                        html = test.text
            else:
                html = test.text
        except:
            pass
        return html
    def filter_tags(self,htmlstr):
        #先过滤CDATA
        re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
        re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
        re_comment=re.compile('<!--[^>]*-->')#HTML注释
        s=re_script.sub('',htmlstr) #去掉SCRIPT
        s=re_style.sub('',s)#去掉style
        s=re_comment.sub('',s)#去掉HTML注释
        #去掉多余的空行
        return s

    def test(self,url='https://zhidao.baidu.com/question/2010715329574801228.html',step_one=[]):
        #可以随意增加字符串过滤条件，step_one的匹配结果要包含step_two，step_two要包含step_three依次类推
        #最后一步一定要匹配标签
        html = self.get_text(url)
        html =  self.filter_tags(html)
        #加第三个参数，多个结果指定选取第几个结果
        #step_one =[('<meta http-equiv="X-UA-Compatible" content="IE=','<link rel="icon" sizes="any" mask href="//www.baidu.com/img/baidu.svg" />'),
                #   ('<meta name="referrer" content="always" />',"</title>")]#第一个元素是已什么字符串开始匹配，第二个元素是以什么字符串结束
        html_list =[]
        html_list.append(html)
        find_flag =1
        for count,item in enumerate(step_one):
            if not len(item[0]) or not len(item[1]):#其中一个条件不匹配
                #记录step_one[count]的错误记录
                pass
            if '|' in item[0]:#代表正则或关系
                split_rule = item[0].split('|')
                re_math = ("(.*)" + item[0] + '|').join(split_rule)
                re_math = ('?i')+re_math + ("(.*)" + item[0])
            else:#没有或关系
                re_math = '(?i)%s(.*)%s'%(item[0],item[1])

            tmp_list = []
            for result in html_list:
                tmp= re.findall(re_math,result,re.DOTALL)#匹配所有
                if len(tmp):
                    for i in tmp:
                        tmp_list.append(i)#将搜索出来的字符串全部添加到列表中
            if not len(tmp_list):
                print ('没有找到匹配结果')
                find_flag =0
                break#没有找到匹配
                #记录错误的步骤
            html_list = tmp_list
        if find_flag:
            for ret in html_list:
                return ret.split(step_one[-1][1])[0]#用最后一个条件最为分割条件

        return 0
    #负责过滤url不符合条件的返回0
    def filter_url(self,url):
        url = url.replace('//', "(|-|)")
        res_list = url.split('/')  # 将url拆分成域名与目录，文件
        domain = res_list[0].replace("(|-|)","//")#域名
        flag = True
        dirct = "/".join(res_list[1:-1])#目录
        file = res_list[-1]#文件

        for item in self.domain_list:
            if item not in domain:
                flag =False
        for item in self.dirct_list:
            if item not in dirct:
                flag = False
        for item in self.file_name:
            if item not in file:
                flag = False

        for item in self.domain1_list:
            if item in domain:
                flag = False
        for item in self.dirct1_list:
            if item in dirct:
                flag = False
        for item in self.file1_name:
            if item  in file:
                flag = False

        return flag

    #获取入口url的全部深度链接
    def get_all_link(self,input_url="http://www.39.net/",Task_Deep=1):
        all_link = []
        tmp_link = []
        html = self.get_text(input_url)
        pagesoup = BeautifulSoup(html, 'lxml')
        for link in pagesoup.find_all(name='a', attrs={"href": re.compile(r'^http:')}):
            url = link.get('href')
            if self.filter_url(url):
                all_link.append(url)
        all_link = list(set(all_link))
        tmp_link = copy.copy(all_link)
        print(len(all_link))
        inner_link = []
        for _ in range(Task_Deep - 1):  # 循环深度大于1
            for link in tmp_link:
                html = self.get_text(link)
                pagesoup = BeautifulSoup(html, 'lxml')
                for inner in pagesoup.find_all(name='a', attrs={"href": re.compile(r'^http:')}):
                    url = inner.get('href')
                    if self.filter_url(url):
                        inner_link.append(url)
            tmp_link = list(set(inner_link))
            inner_link = []
            all_link.extend(tmp_link)
        return list(set(all_link))
if __name__ =='__main__':
    a =  crawl_obj()
    a.run()
    """
    a1 = 'http://news.39.net/hsp/150325/4597046.html'
    html = a.get_text(a1)
    html = a.filter_tags(html)

    #b = a.test(a1,  [['<meta name="Keywords" content="(.*)>|<meta name="Description" content="', '>']])
    b = '<meta name="Description" content="(.*)>|<meta name="Keywords" content="(.*)>'
    tmp = re.findall(b, html, re.DOTALL)  # 匹配所有
    print(tmp)
    #http://corp.39.net/info/disclaimer.html
    """


