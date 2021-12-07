import telnetlib
import time


class TelnetClient:
    def __init__(self):
        self.tn = telnetlib.Telnet()

    def input(self, cmd):
        self.tn.write(cmd.encode('ascii') + b'\n')

    def get_output(self, sleep_seconds=2):
        time.sleep(sleep_seconds)
        return self.tn.read_very_eager().decode('ascii')

    def login(self, host_ip, username, password):
        try:
            self.tn.open(host_ip)
        except:
            print('连接失败')
        # self.tn.read_until(b'login: ')
        # self.input(username)
        self.tn.read_until(b'Password: ')
        self.input(password)
        login_result = self.get_output()
        print(login_result)
        # self.tn.read_until(b'Router> ')
        self.input('en')
        self.tn.read_until(b'Password: ')
        self.input(password)
        login_result = self.get_output()
        print(login_result)
        if 'Login incorrect' in login_result:
            print('用户名或密码错误')
            return False
        print('登陆成功')
        # 持久化连接终端
        self.tn.interact()
        return True

    def logout(self):
        self.input('exit')

    def exec_cmd(self, cmd):
        self.input(cmd)
        res = self.get_output()
        print("===================")
        print(res)
        print("===================")
        return res

    def setPortIp(self, portName, portIP, netmask):
        self.exec_cmd('int %s' % portName)
        self.exec_cmd('ip address %s %s' % (portIP, netmask))
        # 如果是串口，还需要设置时钟
        if portName[0].upper() == 'S':
            self.exec_cmd('clock rate 128000')
        self.exec_cmd('no shutdown')


if __name__ == '__main__':
    tc = TelnetClient()
    tc.login('172.16.0.4', '', 'CISCO')
    tc.exec_cmd('show running-config')
    tc.logout()