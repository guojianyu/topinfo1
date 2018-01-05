#coding=utf-8
from selenium import webdriver
import time,re
import DB_Connect
import urllib.parse
import datetime
import config
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
import random
from selenium.webdriver.common.action_chains import ActionChains #引入ActionChains鼠标操作类
from html.parser import HTMLParser
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.links = []
    def handle_starttag(self, tag, attrs):
        #print "Encountered the beginning of a %s tag" % tag
        if tag == "a":
            if len(attrs) == 0:
                pass
            else:
                for (variable, value) in attrs:
                    if variable == "href":
                        if  'http' in value or 'https' in value:
                            self.links.append(value)


class AccessBaidu(object):
    # os.environ['MOZ_HEADLESS'] = '1'  #headless模式
    """
    selenium在百度中的操作集合
    """
    def __init__(self,ip='localhost',addr='中国',UA ='Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'):
        options = webdriver.ChromeOptions()
        # 更换头部
        options.add_argument('user-agent=%s'%(UA))

        self.driver = webdriver.Chrome(chrome_options=options)

        self.driver.maximize_window()#最大化浏览器
        #self.driver.get('http://httpbin.org/ip')
        #time.sleep(20)
        self.driver.delete_all_cookies()#清理全部cookie
        self.driver.set_page_load_timeout(40)#超时退出
        self.IP=ip
        self.UA = UA
        self.db_opt = DB_Connect.task_opt()#实例化数据库操作对象
        self.Click_Area = addr

    def friendly_link(self,url,Find_URL):#友情链接
        self.driver.get(url)
        flag = 0
        time.sleep(random.uniform(1, 3))  # 点击搜索
        self.scrollrdm()  # 随机滚动
        condition = "//a[contains(text(),%s)]" % (Find_URL)  # 找到关键字
        a_list = self.driver.find_elements_by_xpath(condition)
        for a in a_list:  # 遍历所有a对象
            if Find_URL in a.get_attribute('href'):
                self.driver.execute_script("arguments[0].scrollIntoView();", a)  # 将鼠标定位到该位置
                time.sleep(random.uniform(1, 2))
                flag += 1
                break
        if flag:  # 找到匹配字符串
            a.click()  # 点击链接
        else:  # 没找到直接返回
            return 0
        time.sleep(random.uniform(1, 3))
        # 切换窗口
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])  # 从百度窗口切换到搜索关键字的官网
        return 1

    def openweb_proxy(self, url, ip, port=18080):
        '''
        加http代理打开浏览器并加载首页，设定selenium隐式等待5秒
        :param url:
        :param ip:
        :param port:
        :return:
        '''
        self.url = url
        profile = webdriver.FirefoxProfile()
        profile.set_preference('network.proxy.type', 1)
        profile.set_preference("network.proxy.share_proxy_settings", True)
        profile.set_preference("network.http.use-cache", False)
        profile.set_preference('network.proxy.http', ip)
        profile.set_preference('network.proxy.http_port', port)
        profile.set_preference('network.proxy.ssl', ip)
        profile.set_preference('network.proxy.ssl_port', port)
        profile.set_preference("network.proxy.no_proxies_on", "localhost")

        #启动设置firefox启动项
        profile.set_preference("browser.startup.homepage", "about:blank")
        profile.set_preference("browser.startup.homepage_override.mstone", "ignore")
        profile.set_preference("startup.homepage_welchome_url", "about:blank")
        profile.set_preference("startup.homepage_welcome_url.additional", "about:blank")
        profile.assume_untrusted_cert_issuer=True
        profile.accept_untrusted_certs=True
        # profile.set_preference("permissions.default.image", 2) #禁止加载图片
        profile.set_preference("browser.migration.version", 9001)

        profile.update_preferences()
        self.driver = webdriver.Firefox(firefox_profile=profile)
        try:
            self.driver.implicitly_wait(20)
            self.driver.get(self.url)
            return True
        except Exception as e:
            print (e)

    def move_mouse(self):
        article = self.driver.find_element_by_link_text()
        ActionChains(self.driver).move_to_element(article).perform()  # 将鼠标移动到这里，但是这里不好用
        ActionChains(self.driver).context_click(article).perform()

    def input_mainpage(self):  # 进入含有广告的主页，返回2个广告url
        print('input_mainpage')
        main_page_deep = random.choice(range(1, config.MAIN_PAGE_DEEP+1))  # 随机深度
        print('深度', main_page_deep)
        has_advert = 0  # 上层是否有广告
        tmp_id_list = 0
        tmp_advert_div_id =0
        for main_page_num in range(main_page_deep):
            page_url_list = []  # 存放非百度的URL
            page_url_list.append(self.driver.current_url)
            id_list = []
            advert_num = 0
            advert_div_id = []
            time.sleep(random.uniform(3, 5))
            condition = "//a"  # 找到关键字
            page_source = self.driver.find_elements_by_xpath(condition)
            for i in page_source:
                u = i.get_attribute('href')
                if u and 'almightycell.cn/' in u and 'html' in u:
                    page_url_list.append((i, u))  # 将对象与url存放
            page_res = random.choice(page_url_list)
            print(page_res)
            if type(page_res) == tuple:  # 如果是首页不要动
                time.sleep(2)
                self.driver.execute_script("arguments[0].scrollIntoView();", page_res[0])  # 将鼠标定位到该位置
                time.sleep(random.uniform(1, 2))
                self.driver.get(page_res[1])  # 请求本页其他url
                time.sleep(random.uniform(3,5))

            advert_iframe = self.driver.find_elements_by_xpath("//div/iframe")  # 找到iframe
            for i in advert_iframe:
                if i.get_attribute('id').startswith('iframeu'):  # 找到百度iframe
                    try:
                        advert_num += 1
                        self.driver.switch_to.default_content()
                        div_iframe_id = self.driver.find_element_by_id(i.get_attribute('name')).find_element_by_xpath(
                            '..').get_attribute('id')
                        id_list.append((div_iframe_id, self.driver.find_element_by_id(div_iframe_id)))
                        advert_div_id.append(div_iframe_id)
                    except Exception as e:
                        print(e)
                        pass
            if advert_num > 0: #有广告
                has_advert = advert_num  # 记录广告数
                tmp_id_list = id_list
                tmp_advert_div_id = advert_div_id
            else:  # 没有广告，
                if has_advert:  # 上一层有广告，上翻
                    break

        advert_num = has_advert
        id_list = tmp_id_list
        advert_div_id = tmp_advert_div_id
        if advert_num == 0:  # 在页面搜索没有找到广告页
            # 写错误日志
            print('在页面搜索没有找到广告页')
            return 0
        print('搜索到广告页')

        url_list = []  # 存放全部的广告url
        for advert in id_list:  # 遍历广告iframe,依次取出每个iframe对应的href
            self.driver.switch_to.default_content()
            advert1 = advert[1].find_element_by_tag_name("iframe")  # 找到iframe
            self.driver.switch_to.frame(advert1)
            condition = "//*[@href]"
            element = "href"
            for link in self.driver.find_elements_by_xpath(condition):
                if 'http' in link.get_attribute(element) or 'https' in link.get_attribute(element):
                    url = link.get_attribute(element)
                    if self.filter_baidu(url):
                        text = link.get_attribute('text').strip()
                        url_list.append((advert[0], url, text))  # 将所有的div id url添加到列表
        self.ADS_Zone_Total = advert_num  # 获取的广告数量
        res_list = random.sample(url_list,config.CLICK_AD_NUM)
        self.driver.switch_to.default_content()  # iframe 切回主视图
        return res_list,advert_div_id


    def baidu_key(self,key_word,Find_URL):#点击关键字
       # key_word = u"干细胞"
        self.driver.get('https://www.baidu.com/')
        flag = 0
        self.driver.find_element_by_id("kw").send_keys(key_word)
        #输入关键字
        time.sleep(random.uniform(1, 2))  # 点击搜索
        self.driver.find_element_by_id("su").click()
        time.sleep(random.uniform(1,3))#点击搜索
        #self.scrollrdm()#随机滚动
        condition = "//a[contains(text(),%s)]" % (Find_URL)#找到关键字
        a_list = self.driver.find_elements_by_xpath(condition)
        for a in a_list:#遍历所有a对象
            if Find_URL in a.get_attribute('text'):
                #self.driver.execute_script("arguments[0].scrollIntoView();", a)#将鼠标定位到该位置
                time.sleep(random.uniform(1, 2))
                flag +=1
                break
        if flag:#找到匹配字符串
            a.click()#点击链接
        else:#没找到直接返回
            #写入错误日志
            return 0
        time.sleep(random.uniform(1, 3))
        #切换窗口
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])#从百度窗口切换到搜索关键字的官网
        return 1

    def scrollBot(self):#模拟滚动,将滚动条滚到底部
        # 将页面滚动条拖到
        try:
            js = "var q=document.documentElement.scrollTop=10000"
            self.driver.execute_script(js)
            time.sleep(random.uniform(1,3))
        except:
            pass

    def scrollrdm(self):#随机滚动到某一位置
        try:
            js = "var q=document.documentElement.scrollTop=%s"%(random.randint(1,10000))
            self.driver.execute_script(js)
            time.sleep(random.uniform(1, 3))
        except:
            pass

    def scrollTop(self):  # 模拟滚动,将滚动条滚到顶部
        # 将页面滚动条拖到
        try:
            js = "var q=document.documentElement.scrollTop=0"
            self.driver.execute_script(js)
            time.sleep(random.uniform(1,3))
        except:
            pass
    def back(self):#网页后退
        self.driver.back()
    def quit(self):
        self.driver.quit()
    def accept_arg(self,task_id,site_id):#接受参数方法
        self.task_id = task_id
        self.site_id = site_id
    def jump_url(self,url_list,advert_div_id):#跳转url,参数为一个url列表，函数会一次访问并跳转,第二个参数为深度，点击广告以后进入多深
        print ('jump_url')
        deep = random.choice(range(1,config.CLICK_AD_DEEP+1))
        Click_URL = self.driver.current_url  # 当前url
        add_flag = 0
        for id, url,url_text in url_list:
            time.sleep(2)
            ad = advert_div_id.index(id)+1#广告词所在区域
            print ('广告区域',ad)
            WebDriverWait(self.driver,5).until(lambda driver: driver.find_element_by_id(id))
            menu = self.driver.find_element_by_id(id)
            self.driver.execute_script("arguments[0].scrollIntoView();", menu)
            self.driver.get(url)  # 随机跳转网页
            time.sleep(2)
            ads_title = re.findall(r"d=(.+?)&", self.driver.current_url)#解析出来标题
            ads_title = urllib.parse.unquote(ads_title [0])
            print (ads_title)
            #访问成功然后写日志
            Task_ID = self.task_id
            Site_ID = self.site_id
            ADS_Zone_Total =self.ADS_Zone_Total
            Click_No = ad#点击区域
            Click_Time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            Click_IP = self.IP
            Click_UA = self.UA
            Click_Area = self.Click_Area
            ADS_Title = ads_title
            ADS_URL = url
            if add_flag ==0:
                add_flag +=1
                self.db_opt.click_advert_add(Task_ID)#点击表加1
            log = (Task_ID,Site_ID,ADS_Zone_Total,Click_No,Click_URL,Click_Time,Click_IP,Click_UA,Click_Area,ADS_Title,ADS_URL)
            print (log)
            self.db_opt.click_advert_log(log)
            print ('写入日志')
            self.scrollrdm()  # 进入广告页然后随机滚动
            time.sleep(random.uniform(3, 5))
            for item in range(deep):
                condition = "//h3/a"  # 找到关键字
                ran_num = random.choice(range(3))
                tmp_num = 0
                a_list = self.driver.find_elements_by_xpath(condition)
                for i in a_list:
                    try:
                        if 'http:' in i.get_attribute('href') or 'https:' in i.get_attribute('href'):
                            if ran_num == tmp_num:
                                i.click()
                                time.sleep(random.uniform(2, 4))
                                windows = self.driver.window_handles
                                self.driver.switch_to.window(windows[-1])  # 从百度窗口切换到搜索关键字的官网
                                time.sleep(random.uniform(1, 2))
                                break
                            tmp_num +=1
                    except :
                        pass
            windows = self.driver.window_handles
            print('切换到第二个窗口')
            self.driver.switch_to.window(windows[1])  # 从百度窗口切换到搜索关键字的官网
            time.sleep(random.uniform(1, 2))

    def filter_baidu(self,url):#开启url过滤,该函数可根据需求改动
        if 'baidu'in url and '.js' not in url and '.css' not in url:#找到url含有百度的链接
            if len(re.findall(r"d=(.+?)&", url))>0:#时广告链接
                return 1
        return 0

    def set_referer(self,url='http://www.baidu.com'):
        self.driver.add_argument('--referer=%s'%(url))
if __name__ =="__main__":
    obj = AccessBaidu()
    obj.baidu_key("干细胞 慢病管理",'almightycell.cn')
   # res_url, advert_div_id = obj.input_mainpage()#参数1随机返回的广告div id 和url,返回值2 顺序的广告div 列表
    #print (res_url)
    #obj.jump_url(res_url,advert_div_id)  # 跳转广告，然后返回主页
    #obj.quit()
    """
    res_url = obj.input_mainpage()
    # 模拟人为操作
    obj.scrollBot()#拉到最下
    obj.scrollTop()#拉到最上
    obj.scrollrdm()#随机滚动
    obj.jump_url( res_url)#跳转广告，然后返回主页
    #obj.scrollrdm()#随机滚动
    """


    #obj.back()
    #obj.quit()
