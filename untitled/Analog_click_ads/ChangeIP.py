#使用VPS服务器接收代理IP
import paramiko,time,requests,json
class SSHConnection(object):
    def __init__(self, host,port, username='', pwd=''):
        self.host = host
        self.port = port
        self.username = username
        self.pwd = pwd
        self.__k = None

    def run(self):
        self.connect()  # 连接远程服务器
        server_stop_cmd = 'pppoe-stop'
        server_start_cmd = 'pppoe-start'
        KillProxy = "/bin/bash -c 'ps -ef | grep proxy | grep -v grep |cut -c 7-16 | xargs kill -s 9'"
        get_proxy_cmd = "ifconfig ppp0 | grep 'inet addr'| awk '{ print $2}' | awk -F: '{print $2}'"
        self.cmd(server_stop_cmd)  # 停止服务
        time.sleep(3)
        self.cmd(server_start_cmd)  # 开始服务
        time.sleep(3)
        ip= self.cmd(get_proxy_cmd)#得到新ip
        ip = self.parser_cmd_stdout(ip)
        self.cmd(KillProxy)
        time.sleep(3)
        ProxyRise = "python proxy.py --hostname %s --port 18080" % ip
        self.cmd(ProxyRise)
        self.close()  # 关闭连接
        return  self.get_ip(ip)

    def connect(self):
        self._transport = paramiko.Transport((self.host, self.port))
        self._transport.connect(username=self.username, password=self.pwd)
        self.ssh = paramiko.SSHClient()
        self.ssh._transport = self._transport
    def close(self):
        self._transport.close()

    def upload(self, local_path, target_path):
        sftp = paramiko.SFTPClient.from_transport(self._transport)
        sftp.put(local_path, target_path)

    def cmd(self, command):
        # 执行命令
        stdin, stdout, stderr = self.ssh.exec_command(command)
        return stdout
    def parser_cmd_stdout(self,stdout):
        # 获取命令结果
        result = stdout.read().decode('utf-8').strip()
        return result

    def get_ip(self,ip_dd):
        ip = 'ip'
        address = 'address'
        proxies = {'http': 'http://%s:18080' % ip_dd, 'https': 'https://%s:18080' % ip_dd}
        r = requests.get('http://ip.chinaz.com/getip.aspx', proxies=proxies)
        get = r.text
        get =eval(get)
        #dic = eval(get)
        return get
if __name__ == '__main__':
    ip="222.223.123.94"
    port =20097
    user = 'root'
    pwd = '3088348'
    obj = SSHConnection(ip,port,user,pwd)
    addr_ip = obj.run()
    print (addr_ip['address'])
    print (addr_ip['ip'])
