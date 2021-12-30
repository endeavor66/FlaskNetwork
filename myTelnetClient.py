import telnetlib
import time


class TelnetClient:
    def __init__(self, host_ip, password):
        self.tn = telnetlib.Telnet()
        self.host_ip = host_ip
        self.password = password

    def input(self, cmd):
        self.tn.write(cmd.encode('ascii') + b'\n')

    def get_output(self, sleep_seconds=2):
        time.sleep(sleep_seconds)
        return self.tn.read_very_eager().decode('ascii')

    def login(self):
        try:
            self.tn.open(self.host_ip)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print('连接失败')
            return False
        self.tn.read_until(b'Password: ')
        self.input(self.password)
        login_result = self.get_output()
        print(login_result)
        self.input('en')
        self.tn.read_until(b'Password: ')
        self.input(self.password)
        login_result = self.get_output()
        print(login_result)
        if 'Login incorrect' in login_result:
            print('用户名或密码错误')
            return False
        print('登陆成功')
        return True

    def logout(self):
        self.input('exit')

    def exec_cmd_without_login_logout(self, cmd):
        try:
            if cmd == 'show ip ospf database':
                self.input("terminal length 0")
                login_result = self.get_output()
                print(login_result)
            self.input(cmd)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return
        res = self.get_output()
        print(res)
        return res

    def exec_cmd(self, cmd):
        try:
            self.login()
            if cmd == 'show ip ospf database':
                self.input("terminal length 0")
                login_result = self.get_output()
                print(login_result)
            self.input(cmd)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return
        res = self.get_output()
        self.logout()
        print(res)
        return res

    def setPortIp(self, portName, portIP, netmask):
        self.exec_cmd_without_login_logout('conf t')
        self.exec_cmd_without_login_logout('int %s' % portName)
        self.exec_cmd_without_login_logout('ip address %s %s' % (portIP, netmask))
        # 如果是串口，还需要设置时钟
        if portName[0].upper() == 'S':
            self.exec_cmd_without_login_logout('clock rate 128000')
        self.exec_cmd_without_login_logout('no shutdown')


