"""
vpn_file = 'vpnip.py'
import os,time
print (os.getcwd())
print (os.path.join(os.getcwd(),vpn_file))
cmd = "python36 %s"%os.path.join(os.getcwd(),vpn_file)
print (cmd)
os.system(cmd)#更换代理
time.sleep(10)
"""

#a_list.click()
#chrome.quit()


import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
# 进入浏览器设置
options = webdriver.ChromeOptions()
# 设置中文
# 更换头部

browser = webdriver.Chrome()
a = '干细胞 慢病管理'
url = "https://www.baidu.com/"
browser.get('https://www.baidu.com/')
input = browser.find_element_by_id("kw")
for i in a:
    print (i)
    input.send_keys(i)
    time.sleep(0.2)
input.send_keys(Keys.RETURN)
browser.find_element_by_id("su").click()
#browser.quit()
