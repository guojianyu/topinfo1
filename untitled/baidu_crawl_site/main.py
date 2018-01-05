from lxml import etree
import requests
import DB_Connect
import xlwt
import re
import xlrd
from xlutils.copy import copy
t = DB_Connect.task_opt()
sum_count = 0
while True:
    site_coll = t.look_advert_log()
    data_sum = len(site_coll)
    print (data_sum)
    try:
        excel = xlrd.open_workbook('My Worksheet.xls')
    except:
        print ('hello')
        excel = xlwt.Workbook(encoding = 'ascii')
        worksheet = excel.add_sheet('My Worksheet')
        excel.save('My Worksheet.xls')
        excel = xlrd.open_workbook('My Worksheet.xls')
    readrows = excel.sheets()[0].nrows
    save_sheet =  copy(excel)
    worksheet =save_sheet.get_sheet(0)
    item = 0
    if readrows < data_sum:
        for data in site_coll[readrows:readrows+100]:#取10条数据
            if '.' in data[1]:
                timeout_flag= 0#是否超时标志
                for i in range(3):
                    try:
                        test = requests.get('http://www.baidu.com/s?wd=%s' % 'site:%s' % data[1])
                        root = etree.HTML(test.content)
                        timeout_flag = 0
                        break
                    except:
                        timeout_flag+=1
                if timeout_flag>0:#访问超时
                    worksheet.write(readrows+item, 0, data[0])
                    worksheet.write(readrows+item, 1, data[1])
                    worksheet.write(readrows+item, 2, '0')
                    t.update_crawl_count(data[0],'0')
                    worksheet.write(readrows+item, 3, '访问超时')
                    item += 1
                    sum_count +=1
                    continue
                try:  # 统计搜索个数
                    tmp = root.xpath("//div[@id='content_left']/div[1]/div[1]/p/b/text()")
                    shuzi = re.findall(r"\d+\.?\d*", tmp[0])
                    worksheet.write(readrows+item, 0, data[0])
                    worksheet.write(readrows+item, 1, data[1])
                    worksheet.write(readrows+item, 2, shuzi[0])
                    t.update_crawl_count( data[0],shuzi[0])
                    worksheet.write(readrows+item, 3, '有搜索结果')
                except:
                    try:  # 网站被收录个数
                        tmp = root.xpath(
                            "//div[@id='content_left']/div[1]/div[1]/div[1]/div[1]/p/span/b/text()")
                        worksheet.write(readrows+item, 0, data[0])
                        worksheet.write(readrows+item, 1, data[1])
                        worksheet.write(readrows+item, 2, tmp[0])
                        t.update_crawl_count( data[0],tmp[0])
                        worksheet.write(readrows+item, 3, '网站被收录')
                    except:
                        worksheet.write(readrows+item, 0, data[0])
                        worksheet.write(readrows+item, 1, data[1])
                        worksheet.write(readrows+item, 2, '0')
                        t.update_crawl_count(data[0],'0')
                        worksheet.write(readrows+item, 3, '无效网站')
                item += 1
                sum_count += 1
                print('本次操作总计写入数据个数为：>',sum_count)
            else:
                worksheet.write(readrows + item, 0, data[0])
                worksheet.write(readrows + item, 1, data[1])
                worksheet.write(readrows + item, 2, '0')
                t.update_crawl_count(data[0], '0')
                worksheet.write(readrows + item, 3, '无法解析')
        save_sheet.save('My Worksheet.xls')