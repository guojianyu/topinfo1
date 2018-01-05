import pymssql,datetime,random
class task_opt():
    def __init__(self):
        DB_DICT = {
            #'server': '192.168.1.189',
            'server': '192.168.0.9',
            'user': 'sa',
            'password': 'Q!W@E#R$T%2015q1w2e3r4t5',
            #'database': 'TOPTHEALTH2017'
            'database': 'DBS_Crawl_02'
        }
        self.db_obj =SqlRW(**DB_DICT)#实例化数据库对象

    def insert_Compare_Related(self,Article_RID,Related_Txt):#将相关搜索插入数据库
        sql = "insert into Compare_Related(Article_RID,Related_Txt) VALUES (% r,%r);" % (
            Article_RID,Related_Txt)
        self.db_obj.WriteSql(sql)

    def insert_Compare_List(self,Article_RID,Baidu_URL,Compare_Summary_Baidu,Compare_Description,Compare_Content,Compare_Summary,Compare_Note,Compare_Rate,Compare_Title,Compare_Keywords):#文章临时表
        #sql = "insert into Compare_List(Article_RID,Compare_URL,Compare_Title,Compare_Keywords,Compare_Summary_Baidu,Compare_Description,Compare_Content,Compare_Summary,Compare_Note,Compare_Rate) VALUES (%r,%r,%r,%r,%r,%r,%r,%r,%r,%r);" % (
            #Article_RID, Baidu_URL, Compare_Title.replace("'", '"'), Compare_Keywords.replace("'", '"'),
            #Compare_Summary_Baidu.replace("'", ""), Compare_Description.replace("'", '"'),
            #Compare_Content.replace("'", '"'), Compare_Summary.replace("'", '"'), Compare_Note, Compare_Rate)
        #self.db_obj.WriteSql(sql)

        sql = "insert into Compare_List(Article_RID,Compare_URL,Compare_Title,Compare_Keywords,Compare_Summary_Baidu,Compare_Description,Compare_Content,Compare_Summary,Compare_Note,Compare_Rate) VALUES (%r,%r,%r,%r,%r,%r,%r,%r,%r,%r);" % (
            Article_RID, Baidu_URL, Compare_Title.replace('\u0000', '').replace('\x00', '').replace("'", ""),
            Compare_Keywords.replace('\u0000', '').replace('\x00', '').replace("'", "").replace('“', '').replace('”', "").replace('"', ''),
            Compare_Summary_Baidu.replace('\u0000', '').replace('\x00', '').replace("'", "").replace('“', '').replace('”', "").replace('"', ''),
            Compare_Description.replace('\u0000', '').replace('\x00', '').replace("'", "").replace('“', '').replace('”', "").replace('"', ''),
            Compare_Content.replace('"', '&quot').replace("'", "&apos").replace('“', '&quot').replace('”', "&quot"),
            Compare_Summary.replace("'", '').replace('“', '').replace('”', "").replace('"', ''), Compare_Note.replace('\u0000', '').replace('\x00', '').replace("'", ""),
            Compare_Rate)
        self.db_obj.WriteSql(sql)

    def insert_Article_Tags(self,art_id,tag,rate):#添加名词词频和频率
        sql = "insert into Article_Tags(Article_RID,Article_tag,Article_Rate) VALUES (% r,%r,%r);" % (
        art_id, tag, rate)
        self.db_obj.WriteSql(sql)
    def select_Article_List(self):#自身比较
        Sql_info = "select top 600 RID,Article_Title,Article_Content from Article_list WHERE (isNote=0);" #根据任务ID得到具体任务信息
        result = self.db_obj.ReadSql(Sql_info)
        return result
    def select_compare_Article_List(self):
        Sql_info = "select top 600 RID,Article_Title,Article_Content from Article_list WHERE (isCompare=0);"  # 根据任务ID得到具体任务信息
        result = self.db_obj.ReadSql(Sql_info)
        return result
    def update_compare_flag(self,id,flag='1'):
        sql = "update Article_list set isCompare= %r  WHERE RID=%r;" % (flag, id)
        print(sql)
        self.db_obj.WriteSql(sql)
    def update_Article_List(self,id,note):
        sql = "update Article_list set Article_Note= %r,isNote= 1 WHERE RID=%r;" % (note,id)
        self.db_obj.WriteSql(sql)
    def select_Compare_List(self):#得到获取过文章最大相似度的文章id
        Sql_info = "select * from Compare_List;"  # 根据任务ID得到具体任务信息
        result = self.db_obj.ReadSql(Sql_info)
        return result
    def insert_Article_List_Summary(self,summary,id):
        sql = "insert into Article_Note(Article_RID,Article_Summary) VALUES (%r,%r);" % (id,(summary.replace("'",'').replace('"','')))
        self.db_obj.WriteSql(sql)

    def look_biao(self):
        Sql_info = "select  * from Article_List WHERE (isCompare=1 or isCompare=2);"  # 根据任务ID得到具体任务信息
        result = self.db_obj.ReadSql(Sql_info)
        return result
class SqlRW(object):
    def __init__(self, server, user, password, database):
        self.server = server
        self.user = user
        self.password = password
        self.database = database

    def __GetConnect(self):
        self.conn = pymssql.connect(self.server, self.user, self.password, self.database,charset='utf8')
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
    import time
    t = task_opt()
  #  肝脏:0.23 | 护肝:0.07 | 肝炎:0.06 | 酒精:0.05 | 维生素:0.05 | 肝细胞:0.05 | 食物:0.05 | 解毒:0.05 | 作用:0.04 | 肝病:0.04 | 可以:0.04 | 修复:0.03 | 解酒:0.03 | 蛋白质:0.03 | 功效:0.03 | 养肝护:0.03 | 养肝:0.03 | 功能:0.03 | 代谢:0.03 | 药物:0.03 | ',)
    #t.delt_crawl_info()
    print (len(t.look_biao()))
    """
    start_time = time.time()
    start_len = len(t.look_biao())
    while True:
        if time.time()-start_time >=60:
            start_time = time.time()
            end_len = len(t.look_biao())
            print ('1分钟比对个数：',end_len-start_len)
            start_len = end_len
    """







