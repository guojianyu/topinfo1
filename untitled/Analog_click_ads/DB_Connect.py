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

    def insert_task(self):  # 模拟添加任务
        import datetime
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "insert into ads_click_task(Task_Title,Site_ID,ADS_Zone_Total,ADS_STR,Click_Total,Click_Curr,Creat_Date,Creat_UID,isDelete) " \
              "values(%r,%r,%r,%r,%r,%r,%r,%r,%r)" % ("advert", '1', '4', 'key', '5', '0', dt, "2", "0")
        self.db_obj.WriteSql(sql)
    def get_task(self):#获取任务
        count = 1
        Sql_task = 'select top(%r)* from Ads_Click_Task where (isDelete=0 AND  Click_Total>Click_Curr);' %(count)
        result = self.db_obj.ReadSql(Sql_task)
        return result
    def get_task_info(self,rid):#获取任务详情
        Sql_info = 'select * from Ads_Click_find where (Task_ID=%r AND isDelete=0);'%(rid)#根据任务ID得到具体任务信息
        result = self.db_obj.ReadSql(Sql_info)
        return result
    def click_advert_add(self,rid=2):#Ads_Click_Task中的任务字段加1,参数为任务自增ID
        Sql_info = 'update Ads_Click_Task set  Click_Curr=Click_Curr+1 WHERE RID=%r;' %rid # 根据任务ID得到具体任务信息
        self.db_obj.WriteSql(Sql_info)
    def click_advert_log(self,a):#写日志表
        sql = "insert into Ads_Click_Log(Task_ID,Site_ID,ADS_Zone_Total,Click_No,Click_URL,Click_Time,Click_IP,Click_UA,Click_Area,ADS_Title,ADS_URL)values(%r,%r,%r,%r, %r, %r, %r, %r,%r, %r,%r);" % (
            a[0], a[1], a[2], a[3], a[4], a[5], a[6], a[7], a[8], a[9], a[10]
        )
        self.db_obj.WriteSql(sql)
    def look_advert_log(self):
        Sql_info = 'select * from Ads_Click_Log;'  # 根据任务ID得到具体任务信息
        result = self.db_obj.ReadSql(Sql_info)
        return result
    def del_advert_log(self,id):
        Sql_info = 'delete from Ads_Click_Log WHERE RID=%r;'%id  # 根据任务ID得到具体任务信息
        self.db_obj.WriteSql(Sql_info)
    def ads_click_errlog(self,task_id,ip,stat_id):
        cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        sql = "insert into Ads_Click_ErrLog(Task_ID,Log_IP,Stat_ID,Log_Time) VALUES (%r,%r,%r,%r);"%(task_id,ip,stat_id,cur_time)
        print (sql)
        self.db_obj.WriteSql(sql)
    def look_click_errlog(self):
        Sql_info = 'select * from Ads_Click_ErrLog;'  # 根据任务ID得到具体任务信息
        result = self.db_obj.ReadSql(Sql_info)
        return result
    def get_ads_ua(self):#从数据库获得UA,interval拿取同一UA的间隔事件单位S
        Sql_info = 'select * from Ads_Click_UA WHERE （UA_Type =0 AND UA_Level>1）;'  #得到全部移动端UA
        result = self.db_obj.ReadSql(Sql_info)
        return random.choice(result)#随机返回一个UA

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
        self.conn.close()
        return result

    def WriteSql(self, sql):
        cursor = self.__GetConnect()
        cursor.execute(sql)
        self.conn.commit()
        self.conn.close()
        return 1

if __name__ == "__main__":
    t = task_opt()
    a= t.look_click_errlog()
    print (a)






