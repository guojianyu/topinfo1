#coding=utf-8
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import time,re
import DB_Connect
import urllib.parse
import datetime
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
    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.delete_all_cookies()#清理全部cookie
        self.driver.set_page_load_timeout(30)#超时退出
        #self.driver.set_script_timeout(10)#这两种设置都进行才有效
        self.IP='localhost'
        self.UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
        self.db_opt = DB_Connect.task_opt()#实例化数据库操作对象
        self.Click_Area = '中国'
    def friendly_link(self,url,Find_URL):#友情链接
        self.driver.get(url)
        flag = 0
        time.sleep(random.uniform(1, 3))  # 点击搜索
        self.scrollrdm()  # 随机滚动
        condition = "//a"  # 找到关键字
        a_list = self.driver.find_elements_by_xpath(condition)
        for a in a_list:  # 遍历所有a对象
            try:
                if Find_URL in a.get_attribute('href'):
                    self.driver.execute_script("arguments[0].scrollIntoView();", a)  # 将鼠标定位到该位置
                    time.sleep(random.uniform(1, 2))
                    flag += 1
                    break
            except:
                pass
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
        id_list = []
        advert_num = 0
        advert_div_id = []
        time.sleep(random.uniform(3, 5))  # 点击搜索
        advert_iframe = self.driver.find_elements_by_xpath("//div/iframe")  # 找到iframe
        for i in advert_iframe:
            if i.get_attribute('id').startswith('iframeu'):  # 找到百度iframe
                try:
                    advert_num +=1
                    self.driver.switch_to.default_content()
                    div_iframe_id = self.driver.find_element_by_id(i.get_attribute('name')).find_element_by_xpath(
                        '..').get_attribute('id')
                    id_list.append((div_iframe_id, self.driver.find_element_by_id(div_iframe_id)))
                    advert_div_id.append(div_iframe_id)
                except Exception as e:
                    print(e)
                    pass
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
                        url_list.append((advert[0], url,text))  # 将所有的div id url添加到列表
        self.ADS_Zone_Total = advert_num#获取的广告数量
        res_list = random.sample(url_list, 2)
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

        self.scrollrdm()  # 随机滚动
        condition = "//a[contains(text(),%s)]" % (Find_URL)#找到关键字
        a_list = self.driver.find_elements_by_xpath(condition)
        a_last = ''
        for a in a_list:#遍历所有a对象
            try:
                if Find_URL in a.get_attribute('text'):
                    tmp = a.find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_xpath('..')
                    self.driver.execute_script("arguments[0].scrollIntoView();",tmp )  # 将鼠标定位到该位置
                    time.sleep(random.uniform(3, 5))
                    flag +=1
                    a_last = a
                    break
            except:
                pass
        if flag:#找到匹配字符串
            print('find')
            a.click()#点击链接
        else:#没找到直接返回
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
    def jump_url(self,url_list,advert_div_id,deep=2):#跳转url,参数为一个url列表，函数会一次访问并跳转,第二个参数为深度，点击广告以后进入多深
        Click_URL = self.driver.current_url  # 当前url
        for id, url,url_text in url_list:
            self.driver.switch_to.default_content()
            time.sleep(2)
            ad = advert_div_id.index(id)+1#广告词所在区域
            print ('广告区域',ad)
            menu = self.driver.find_element_by_id(id)
            self.driver.execute_script("arguments[0].scrollIntoView();", menu)
            WebDriverWait(self.driver, 5).until(lambda driver: driver.find_element_by_id(id))
            a = menu.find_element_by_tag_name('iframe')
            self.driver.switch_to.frame(a)
            time.sleep(3)
            condition = "//*[@href]"
            element = "href"
            for link in self.driver.find_elements_by_xpath(condition):
                if 'http' in link.get_attribute(element) or 'https' in link.get_attribute(element):
                    url1 = link.get_attribute(element)
                    if url == url1:
                        print ('hahaha')
                        print (url)
                        print(link.find_element_by_xpath('..').find_element_by_xpath('..').find_element_by_xpath('..').get_attribute('class'))
                        #find_element_by_xpath('..').get_attribute('class')
                        WebDriverWait(self.driver, 20).until(lambda driver:link)
                        try:
                            link.click()#普通文本广告
                        except:
                            link.find_element_by_xpath('..').find_element_by_xpath('..').click()#图片广告
                            pass
                        time.sleep(5)
                        windows = self.driver.window_handles
                        print('切换到第二个窗口')
                        self.driver.switch_to.window(windows[1])  # 从百度窗口切换到搜索关键字的官网
                        break
            #self.driver.get(url)  # 随机跳转网页
            time.sleep(2)

    def filter_baidu(self,url):#开启url过滤,该函数可根据需求改动
        if 'baidu'in url and '.js' not in url and '.css' not in url:#找到url含有百度的链接
            if len(re.findall(r"d=(.+?)&", url))>0:#时广告链接
                return 1
        return 0

    def set_referer(self,url='http://www.baidu.com'):
        self.driver.add_argument('--referer=%s'%(url))
if __name__ =="__main__":
    obj = AccessBaidu()
    #a = obj.baidu_key("干细胞 慢病管理",'almightycell.cn')
    obj.friendly_link('http://www.kuaimei.cc/','almightycell.cn')
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
