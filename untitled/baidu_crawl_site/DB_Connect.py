import pymssql,datetime,random
class task_opt():
    def __init__(self):
        DB_DICT = {
            'server': '192.168.1.189',
            #'server': '192.168.0.8',
            'user': 'sa',
            'password': 'Q!W@E#R$T%2015q1w2e3r4t5',
            'database': 'TOPTHEALTH2017'
        }
        self.db_obj =SqlRW(**DB_DICT)#实例化数据库对象

    def look_advert_log(self):
        Sql_info = 'select * from crawl_site WHERE (isDelete=0 AND  Count_Baidu_Index=0) ORDER BY RID;' # 根据任务ID得到具体任务信息
        result = self.db_obj.ReadSql(Sql_info)
        return result

    def update_crawl_count(self,id,search_count,type):  # Ads_Click_Task中的任务字段加1,参数为任务自增ID
        Sql_info = 'update crawl_site set Count_Baidu_Index=%s ,Count_Baidu_Type=%s WHERE RID=%s;'% (search_count,type,id)  # 根据任务ID得到具体任务信息
        self.db_obj.WriteSql(Sql_info)
class SqlRW(object):
    def __init__(self, server, user, password, database):
        self.server = server
        self.user = user
        self.password = password
        self.database = database

    def __GetConnect(self):
        self.conn = pymssql.connect(self.server, self.user, self.password, self.database)
        cursor = self.conn.cursor()
        if not cursor:
            print ('connected failed')
        return cursor

    def ReadSql(self,sql):
        cursor = self.__GetConnect()
        cursor.execute(sql)
        result = cursor.fetchall()
        return result

    def WriteSql(self, sql):
        cursor = self.__GetConnect()
        cursor.execute(sql)
        self.conn.commit()
        return 1

    def close_connect(self):
        self.conn.close()
if __name__ == "__main__":
    t = task_opt()
    a = t.look()
    print(len(a))





