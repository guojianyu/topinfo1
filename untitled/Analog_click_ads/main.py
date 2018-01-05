import num_one
import DB_Connect
import ChangeIP
import config
import time,os,requests
def main():
    import random
    t = DB_Connect.task_opt()
    first = 0
    excute_time = time.time()
    time_delay = random.randint(10, 20)  # 休眠10 到 20 分钟
    while True:
        if first>0:
            if excute_time +time_delay*60 >= time.time():
                time.sleep(1)
                print('休眠',time_delay,'分钟')
                continue
        try:
            first+=1
            excute_time = time.time()
            time_delay = random.randint(config.Crawl_interval_time[0], config.Crawl_interval_time[1])  # 休眠10 到 20 分钟
            print('休眠', time_delay, '分钟')
            start_time = time.time()
            if config.PROXY_TYPE[1] == 'vps':#使用拨号服务器
                print ("选用了vps服务器")
                proxy_obj = ChangeIP.SSHConnection(config.VPS_IP, config.VPS_PORT, config.VPS_USER, config.VPS_PWD)  # 代理对象
                addr_ip = proxy_obj.run()#获取代理ip及其所在地
            else:#使用软件vpn
                print("使用VPN软件")
                vpn_file = 'vpnip.py'
                cmd = "python36 %s" % os.path.join(os.getcwd(), vpn_file)
                print(cmd)
                os.system(cmd)  # 更换代理
                time.sleep(30)
                r = requests.get('http://ip.chinaz.com/getip.aspx')
                get = r.text
                addr_ip = eval(get)
            ip = addr_ip['ip']
            addr = addr_ip['address']
            UA = t.get_ads_ua()[2]#获取浏览器
            print ('代理ip:  ',ip,'代理所在地址：',addr,'浏览器：',UA)
            print ('获取代理用时：',time.time()-start_time)
        except:#获取代理异常
            print('代理获取失败')
            continue
        try:
            task = t.get_task()[0]  # 查找到任务
            print(task)
            task_id = task[0]#任务ID
            site_id = task[2]#站点id
            inp_task = t.get_task_info(task_id)  # 根据任务RID取到该类型任务的入口
            print (inp_task)
            if not len(inp_task):  # 该任务没有正常的入口
                continue
            click_task = random.choice(inp_task)  # 得到随机选出的入口
            Find_Type = click_task[3]  # 入口类型
            Start_URL = click_task[4]
            Find_URL = click_task[6]  # 查找的特征字符串
            script_obj = num_one.AccessBaidu(ip,addr,UA)  # 爬虫操作对象
            script_obj.accept_arg(task_id,site_id)#向该对象传递参数
            if Find_Type == 0:  # 搜索引擎进入
                print('搜索引擎')
                Find_Keyword = click_task[5]  # 关键字
                # 判断搜索引擎
                success_flag = script_obj.baidu_key(Find_Keyword, Find_URL)  # 通过搜索引擎
                if not success_flag:  # 第一页没匹配到特征字符串
                    print ('首页匹配关键字失败')
                    #3:没找到匹配字符
                    t.ads_click_errlog(task_id,ip,3)
                    script_obj.quit()
                    continue
                advert_res= script_obj.input_mainpage()  # 进入广告页，返回广告列表
                if type(advert_res) == tuple:
                    res_url, advert_div_id = advert_res
                else:#没有找到广告
                    #1:随机深度没有找到广告
                    t.ads_click_errlog(task_id, ip,1)
                    continue
                script_obj.jump_url(res_url, advert_div_id)  # 跳转广告，然后返回主页
                script_obj.quit()
            else:  # 友情链接进入
                print('友情链接')
                success_flag = script_obj.friendly_link(Start_URL, Find_URL)
                if not success_flag:  # 第一页没匹配到特征字符串
                    script_obj.quit()
                    print('首页匹配关键字失败')
                    t.ads_click_errlog(task_id, ip, 3)
                    script_obj.quit()
                    continue
                advert_res = script_obj.input_mainpage()  # 进入广告页，返回广告列表
                if type(advert_res) == tuple:
                    res_url, advert_div_id = advert_res
                else:  # 没有找到广告
                    # 1:随机深度没有找到广告
                    t.ads_click_errlog(task_id, ip, 1)
                    continue
                script_obj.jump_url(res_url, advert_div_id)  # 跳转广告，然后返回主页
                script_obj.quit()
                pass
            print ('总计用时:',time.time()-start_time)
        except Exception as e:
            print (e)
            #2:加载页面超时
            t.ads_click_errlog(task_id, ip,2)
            script_obj.quit()

if __name__ =="__main__":
    main()
    """
    import datetime
    dt= datetime.datetime.now()
    dt = dt.strftime("%Y-%m-%d %H:%M")
    print (dt)
    t = DB_Connect.task_opt()
    t.look_advert_log()
    log_content = (2,1,1,'','点击url',dt,'127.0.0.1','点击ua','点击地区','广告标题','广告url')
    """
