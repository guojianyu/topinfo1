#cont一个文件读取数据写入另外一个文件
import xlrd
from xlutils.copy import copy
read = xlrd.open_workbook('My Worksheet3.xls')
write = xlrd.open_workbook('My Worksheet.xls')
all_sheets_list=read.sheet_names()
print("All sheets name in File:",all_sheets_list)
first_sheet=read.sheet_by_index(0)
readrows = read.sheets()[0].nrows
print (readrows)
first_row=first_sheet.row_values(1)
print("First row:",first_row)
writerows = write.sheets()[0].nrows#
write1 = copy(write)
write = write1.get_sheet(0)
for item in range(1,readrows):
    print (item)
    tmp = first_sheet.row_values(item)
    print (tmp)
    write.write(writerows+item, 0,tmp[0])
    write.write(writerows + item, 1,tmp[1] )
    write.write(writerows + item, 2,tmp[2])
#write1.save('My Worksheet.xls')