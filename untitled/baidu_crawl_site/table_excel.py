import xlwt
import  DB_Connect
excel = xlwt.Workbook(encoding='utf-8')
worksheet = excel.add_sheet('My_Worksheet.xls')
t = DB_Connect.task_opt()
site_coll = t.look_advert_log()
item =1
for data in site_coll:
    print (item)
    worksheet.write(item, 0, data[0])
    worksheet.write(item, 1, data[1])
    worksheet.write(item, 2, data[11])
    item +=1

excel.save('My_Worksheet.xls')