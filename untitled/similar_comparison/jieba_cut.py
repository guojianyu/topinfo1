#获取文章的关键词
import math
import jieba.analyse
import DB_Connect
import time
from multiprocessing import Process
def cut_word(article):
    # 这里使用了TF-IDF算法，所以分词结果会有些不同->https://github.com/fxsjy/jieba#3-关键词提取
    res = jieba.analyse.extract_tags(
        sentence=article, topK=20, withWeight=True,allowPOS=('n',))
    return res

def tf_idf(res1=None, res2=None):
    # 向量，可以使用list表示
    vector_1 = []
    vector_2 = []
    # 词频，可以使用dict表示
    tf_1 = {i[0]: i[1] for i in res1}
    tf_2 = {i[0]: i[1] for i in res2}
    res = set(list(tf_1.keys()) + list(tf_2.keys()))
    # 填充词频向量
    for word in res:
        if word in tf_1:
            vector_1.append(tf_1[word])
            if word in tf_2:
                vector_2.append(tf_2[word])
            else:
                vector_2.append(0)
        else:
            vector_1.append(0)
            if word in tf_2:
                vector_2.append(tf_2[word])

    return vector_1, vector_2


def numerator(vector1, vector2):
    #分子
    return sum(a * b for a, b in zip(vector1, vector2))

def denominator(vector):
    #分母
    return math.sqrt(sum(a * b for a,b in zip(vector, vector)))


def run(vector1, vector2):
    try:
        res = numerator(vector1,vector2) / (denominator(vector1) * denominator(vector2))
    except:
        res = 0
    return res

def record_keyword(data,t):
    try:
        for item in data:
            print(item[0])
            titile = item[1]
            content = item[2]
            print ('title:',titile)
            print ('content:',content)
            if not titile:
                titile = ''
            if not content:
                content = ''
            tmp = titile + content
            res1 = cut_word(article=tmp)
            ci_tmp = ''
            for ci in res1:
                ci_tmp = "".join([ci_tmp, ci[0], ":", str(round(ci[1],2)), '|'])
                t.insert_Article_Tags(item[0],ci[0],str(round(ci[1],2)))
            t.update_Article_List(item[0], ci_tmp)
    except Exception as e:
        print (e)

if __name__ =='__main__':
#得到分频词与它的权重
    while True:
        start_time = time.time()
        t = DB_Connect.task_opt()
        data = t.select_Article_List()
        print(len(data))
        sign_count = len(data)//6
        end_count = 0
        tmp_list = []
        if sign_count ==0:
            record_keyword(data,t)
        else:
            for i in range(6):#开启6个进程
                a = data[end_count:end_count + sign_count]
                end_count = end_count + sign_count
                p = Process(target= record_keyword, args=(a,t))
                tmp_list.append(p)
            tmp_list.append(Process(target=record_keyword, args=(data[end_count:], t)))
            for j in tmp_list:
                j.start()
            for item in tmp_list:
                item.join()
            for item in tmp_list:
                item.terminate()



