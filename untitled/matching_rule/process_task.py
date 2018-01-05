from multiprocessing import Process,Queue
import time
import os

def sacn_add_task(myqueue):#获取任务的进程，获取的任务添加到队列
    task = [1,2,3,4,5,6,7]
    for i in task:#填充任务到队列
        myqueue.put(i)
    while True:
        print ('任务队列长度：',myqueue.qsize())
        time.sleep(1)

def kill(pid):
    try:
        a = os.kill(pid,9)
        print( '已杀死pid为%s的进程,　返回值是:%s' % (pid, a))
    except OSError as e:
        print( '没有如此进程!!!')

def excutor_task(i,myqueue,tmp):#执行任务
    while True:
        item = myqueue.get()
        pid = os.getpid()
        tmp.put(pid)
        print ('进程:',i,'获取任务：',item,'填充pid:',pid)
        time.sleep(100)

def listen_process(myqueue,tmp):
    time.sleep(10)
    print (tmp.qsize(),'===')
    #查询数据库，如果在中间表得到暂停字段为暂停则会将该任务关联的进程杀掉，并将运行状态更改为暂停状态。
    #并删除该条数据，没有暂停数据则休息.
    pid = tmp.get()
    kill(pid)
    i=7
    p = Process(target=excutor_task, args=(i, myqueue, tmp))  # 执行任务的进程
    p.start()
    time.sleep(5)
    print(tmp.qsize(), '===')
    #item.terminate()

if __name__ == "__main__":
    tmp_list = []
    myqueue = Queue()
    tmp_queue = Queue()
    tmp_list.append(Process(target=sacn_add_task, args=(myqueue,)))
    for i in range(6):  # 开启6个进程
        p = Process(target=excutor_task, args=(i,myqueue,tmp_queue))#执行任务的进程
        tmp_list.append(p)
    p = Process(target=listen_process,args=(myqueue,tmp_queue))#守护进程负责监控任务
    tmp_list.append(p)
    for item in tmp_list:
        item.start()
    for item in tmp_list:
        item.join()
