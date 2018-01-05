#扫描crawl_site表的url并获取检索的答案个数
import DB_Connect
import time,requests
import re
from lxml import etree
def scan_site():
    sum_count = 0
    t = DB_Connect.task_opt()
    site_coll = t.look_advert_log()
    print (len(site_coll))
    for data in site_coll:
        if '.' in data[1]:
            timeout_flag = 0  # 是否超时标志
            for i in range(3):
                try:
                    test = requests.get('http://www.baidu.com/s?wd=%s' % 'site:%s' % data[1])
                    root = etree.HTML(test.content)
                    timeout_flag = 0
                    break
                except:
                    timeout_flag += 1
            if timeout_flag > 0:  # 访问超时
                t.update_crawl_count(data[0], '0',3)
                sum_count += 1
                continue
            try:  # 统计搜索个数
                tmp = root.xpath("//div[@id='content_left']/div[1]/div[1]/p/b/text()")
                shuzi = re.findall(r"\d+\.?\d*", tmp[0])
                t.update_crawl_count(data[0], shuzi[0],2)
            except:
                try:  # 网站被收录个数
                    tmp = root.xpath(
                        "//div[@id='content_left']/div[1]/div[1]/div[1]/div[1]/p/span/b/text()")
                    t.update_crawl_count(data[0], tmp[0],1)
                except:
                    t.update_crawl_count(data[0], '0',3)
            sum_count += 1
            print('本次操作总计写入数据个数为：>', sum_count  ,  data[0])

if __name__ =='__main__':
    scan_site()