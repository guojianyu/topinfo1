import pymssql
import json
class task_opt():
    def __init__(self):
        DB_DICT = {
            'server': '192.168.1.76',
            #'server': '192.168.0.8',
            'user': 'sa',
            'password': 'Q!W@E#R$T%2015q1w2e3r4t5',
            'database': 'TOPTHEALTH2017'
        }
        self.db_obj =SqlRW(**DB_DICT)#实例化数据库对象

    def select_test(self):
        Sql_info = 'select top 600 Task_URL,Task_On_rule,Task_Out_rule,Task_Deep,Task_Match_field,Task_Match_rule,RID from Crawl_Task WHERE (Task_Status=0);'  # 根据任务ID得到具体任务信息
        result = self.db_obj.ReadSql(Sql_info)
        return result
    def update_ready_status(self,id,flag=1):
        sql = "update Crawl_Task set Task_Status= %r  WHERE RID=%r;" % (flag, id)
        self.db_obj.WriteSql(sql)
    def delete_test(self):
        Sql_info = 'delete from Crawl_Task;'  # 根据任务ID得到具体任务信息
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
    t.delete_test()
    a =[]
    b = t.select_test()[0]
    a.append(b)
    for i in a:
        print (i)
        Task_URL = i[0]
        Task_On_rule= i[1]
        Task_Out_rule =i[2]
        Task_Deep =i[3]
        Task_Match_field =i[4]
        Task_Match_rule =i[5]
        #print (Task_URL,Task_On_rule,Task_Out_rule,Task_Deep,Task_Match_field,Task_Match_rule)
        print (Task_Match_field)
        print (Task_Match_rule)
        print (Task_Match_rule.replace('\\"','"'))
        print (json.loads(Task_Match_rule.replace('\\"','"')))

