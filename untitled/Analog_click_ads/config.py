
Crawl_interval_time = [10,20]#睡眠间隔时间区间
MAIN_PAGE_DEEP = 3#主页随机点击的最大深度
CLICK_AD_NUM = 2#进入主页点击广告的次数
CLICK_AD_DEEP =2#模拟点击的最大广告深度
VPS_IP="222.223.123.94"#代理服务器ip
VPS_PORT =20097#代理服务器端口
VPS_USER = 'root'#服务器用户
VPS_PWD = '3088348'#服务器密码
PROXY_TYPE = {1:'vps',0:'vpn'}#键值为1表示使用该value值的代理方式


"""
数据库ip：192.168.1.189  59.110.16.239
数据库名称：TOPTHEALTH2017
数据库账号：sa
密码：Q!W@E#R$T%2015Q1w2e3r4t5

CREATE TABLE IF NOT EXISTS `Ads_Click_Log`(
   `RID` INT UNSIGNED AUTO_INCREMENT,
   `Task_ID` INT NOT NULL,
   `Site_ID` INT NOT NULL,
	`ADS_Zone_Total` INT NOT NULL,
	`Click_No` INT NOT NULL,
	`Click_URL` VARCHAR(40) NOT NULL,
	`Click_Time` DATE,
	`Click_IP` VARCHAR(40) NOT NULL,
	`Click_UA` VARCHAR(100) NOT NULL,
	`Click_Area` VARCHAR(40) NOT NULL,
	`ADS_Title` VARCHAR(40) NOT NULL,
	`ADS_URL` VARCHAR(40) NOT NULL,
   PRIMARY KEY ( `RID` )
)ENGINE=InnoDB DEFAULT CHARSET=utf8;
"""