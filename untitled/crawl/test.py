import requests,os
import jieba.analyse
from lxml import etree
import json
import DB_Connect


db_obj = DB_Connect.task_opt()
def cut_word(article):
    # 这里使用了TF-IDF算法，所以分词结果会有些不同
    res = jieba.analyse.extract_tags(
        sentence=article, topK=20, withWeight=True)
    return res

hang = 0
for iitem in  range(1,201):
    try:
        dir =str(iitem)
        input  = 'http://gyh.xywy.com/bingyin/list_%s.html'%(iitem)
        test = requests.get(input)
        cur_path = os.getcwd()
        cur_path = os.path.join(cur_path,dir)
        isExists = os.path.exists(cur_path)
        if not isExists:
            os.makedirs(cur_path)
        root = etree.HTML(test.text)
        top_item1 =set()
        #左上
        top_left = root.xpath("//div[@class='fl w299']//a/@href")
        top_right = root.xpath("//div[@class='fl w299 ml26']//a/@href")
        for i in top_left:
            top_item1.add(i)
        for i in top_right:
            top_item1.add(i)
        #右下
        root = etree.HTML(test.text)
        div_obj = root.xpath("//ul[@class='entry-reading mt15 clearfix']//li/div/a/@href")
        for i in div_obj:
            top_item1.add(i)
        #右上
        div_obj = root.xpath("//ul[@class='entry-rightscript']//li/a/@href")
        for i in div_obj:
            top_item1.add(i)
        #左下
        div_obj = root.xpath("//div[@class='entry-name fb mt25']/a/@href")
        for i in div_obj:
            top_item1.add(i)
        #得到全部文章的url
        i =0

        for page_url in top_item1:
            i += 1
            print (i)
            inener_html = requests.get(page_url)  # 请求url
            inner_root = etree.HTML(inener_html.content)
            top_head = inner_root.xpath("//h3[@class='tc fn pt5']/text()")
            print(top_head[0])
            file_name = os.path.join(cur_path, top_head[0])
            top_content = inner_root.xpath("//div[@class='passage pl10 pr10 f14']//p/text()")  # 文章体
            tmp_file = ''
            tmp_file = "".join([tmp_file, top_head[0], '\n'])
            for j in top_content:
                tmp_file = "".join([tmp_file, j, '\n'])
            ciping = cut_word(tmp_file)
            title = top_head[0]
            url = page_url
            content = tmp_file
            ci_tmp = ''
            for ci in ciping:
                ci_tmp = "".join([ci_tmp, ci[0],":",str(ci[1]),'|'])
            db_obj.insert_crawl_info(title, url, content,ci_tmp)

    except:
        pass




