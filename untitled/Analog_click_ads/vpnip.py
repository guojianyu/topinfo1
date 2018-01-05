#使用VPN软件更改本机IP的形式

#按F8更改软件的IP
import win32api
import win32con
import win32gui
import os,time

def change_ip():#点击F8切换IP
    win32api.keybd_event(119, 0, 0, 0)  # F8
    win32api.keybd_event(119, 0, win32con.KEYEVENTF_KEYUP, 0)  # 释放按键

#vpn_path是VPN程序的路径
def check_vpn(vpv_path=r'C:\Users\jay\Desktop\VPN\追星加速器.exe &'):#检查VPN程序有没有启动
    processname = '追星加速器'
    has_flag =0
    for line in os.popen("tasklist"):
        fields = line.split()
        try:
            process = fields[0]
            if processname in process:
                has_flag+=1
        except:
            pass
    if not has_flag:#程序没有启动
        print ('没有启动程序')
        os.popen(vpv_path)
        time.sleep(5)
        print('end programa')
        return 0
    return 1
def start_vpn():#开启VPN程序
    test = '加速器 20170906.8'
    hwnd = win32gui.FindWindow(0, test)
    clsname = win32gui.GetClassName(hwnd)
    clsname = win32gui.GetWindowText(hwnd)
    print(hwnd, 'hehe')
    print(clsname, 'hhaha')
    btn = win32gui.FindWindowEx(hwnd, None, 'Button', None)
    clsname = win32gui.GetClassName(btn)
    print(clsname, 'hhaha')
    win32gui.SetForegroundWindow(hwnd)
    win32gui.PostMessage(btn,win32con.WM_LBUTTONDOWN,win32con.VK_MBUTTON,0)
    win32gui.PostMessage(btn,win32con.WM_LBUTTONUP,win32con.MK_LBUTTON,0)
    #win32gui.PostMessage(btn, win32con.WM_KEYDOWN, win32con.WM_MBUTTONDOWN, 0)
    #win32gui.PostMessage(btn, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
    win32api.keybd_event(13, 0, 0, 0)  # 回车
    win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)
    # time.sleep(1)
    # win32api.keybd_event(13, 0, 0, 0)  # 回车
    # win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)
    # win32api.SendMessage(btn,win32con.WM_LBUTTONDOWN,win32con.MK_LBUTTON,0)
    time.sleep(1)




if check_vpn():#返回值为TRUE程序已经启动
    pass
else: #没有开启程序
    start_vpn()
change_ip()#按F8切换ip
