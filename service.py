import yaml
import json
import ipaddress
from myTelnetClient import TelnetClient as TC

'''
功能：根据配置文件内容，计算拓扑信息
接受：文件内容
返回：拓扑信息，包含：链路信息
'''

'''
功能：根据端口ip和网络掩码，计算网段
'''
def cal_portNetIp(ip):
    host = ipaddress.ip_interface(ip)
    net = host.network
    return net.with_prefixlen

'''
功能：根据路由器的port原始信息，解析得到各个portIP、portNetIp、portStatus
'''
def cal_portsInfo(routerInfo):
    portsInfo = []
    portList = []
    allPorts = ['s0/0/0', 's0/0/1', 'f0/0', 'f0/1']
    for info in routerInfo:
        keys = info.keys()
        portName = list(keys)[0]
        portIP = info[portName]
        portNet = cal_portNetIp(portIP)
        tmp_dic = {
            "name": portName,
            "ip": portIP,
            "net": portNet,
            "status": "up"
        }
        portsInfo.append(tmp_dic)
        portList.append(portName)
    # 对于不在配置文件中的端口，分配默认值
    for p in allPorts:
        if p not in portList:
            tmp_dic = {
                "name": p,
                "ip": 'unassigned',
                "net": 'unassigned',
                "status": "down"
            }
            portsInfo.append(tmp_dic)
    return portsInfo

'''
功能：根据配置信息，解析得到每个路由器的信息
输入：配置信息
输出：路由器信息
路由器信息的数据格式
routerInfo = [
    {
        'name': 'RouterA',
        'ports': [
            {
                'name': 's0/0/0',
                'ip': '192.168.1.2/24', 
                'net': '192.168.1.0/24',
                'status': 'up'
            },
            {
                'name': 's0/0/1',
                'ip': 'unassigned',
                'status': 'down'
            }
        ]
    }
]
'''
def getRouterInfo(content):
    data = yaml.load(content, Loader=yaml.SafeLoader)
    routerInfo = []
    for key, value in data.items():
        rName = key
        rIP = value['ip']
        rPassword = value['password']
        rInfo = value["port"]
        # 获取路由器的所有端口信息，包括端口ip、端口网段、端口状态
        portsInfo = cal_portsInfo(rInfo)
        tmp_dic = {
            "name": rName,
            "ports": portsInfo
        }
        routerInfo.append(tmp_dic)
    return routerInfo

'''
功能：根据所有路由器信息，解析得到链路信息
输入：路由器信息
输出：链路信息
链路信息的数据格式
{
  "from": {
    "name": RouterA,
    "port": s0/0/0,
    "portIP": 192.168.1.2
  },  
  "to": {
    "name": RouterB,
    "port": s0/0/0,
    "portIP": 192.168.1.3
  }  
}
'''
def getConnectionInfo(routerInfo):
    # 计算每个路由器的所有端口网段信息，rt_dic格式： { "name": “RouterA”, "ports": [192.168.1.0, 192.168.2.0]}
    rt_dic = {}
    for r in routerInfo:
        routerName = r["name"]
        nets = []
        portsInfo = r["ports"]
        for p in portsInfo:
            portName = p["name"]
            if portName.startswith("s") or portName.startswith("f"):
                portNet = p["net"]
                # 未配置的端口直接跳过
                if portNet == 'unassigned':
                    continue
                nets.append(portNet)
        rt_dic[routerName] = nets

    # 计算链路信息
    connection = []
    rts = list(rt_dic.keys())
    for i in range(len(rts) - 1):
        for j in range(i+1, len(rts)):
            i_name = rts[i]
            j_name = rts[j]
            i_cons = rt_dic[i_name]
            j_cons = rt_dic[j_name]
            # 判断i和j是否连接，若连接，返回连接的网络名
            con = is_connect(i_cons, j_cons)
            if con is not None:
                # 后面需要加入连接的两个端口信息（将con进行替换）
                fromPort = getPort(routerInfo, i_name, con)
                toPort = getPort(routerInfo, j_name, con)
                tmp_dic = {
                    "from": {
                        "name": i_name,
                        "port": fromPort["name"],
                        "portIP": fromPort["ip"]
                    },
                    "to": {
                        "name": j_name,
                        "port": toPort["name"],
                        "portIP": toPort["ip"]
                    }
                }
                connection.append(tmp_dic)
    return connection

'''
功能：给定两组网络号，判定是否存在链路
输入：两组网络号
输出：链路（没有则返回None）
'''
def is_connect(i_cons, j_cons):
    for v in i_cons:
        if v in j_cons:
            return v
    return None

'''
功能：给定路由器、链路信息，返回链路对应的port信息
输入：路由器、链路信息
输出：port（没有则返回None）
'''
def getPort(routerInfo, router, con):
    port = None
    for r in routerInfo:
        if r["name"] == router:
            for p in r["ports"]:
                if p["net"] == con:
                    port = p
                    break
    return port

'''
功能：获取每个路由器的telnet客户端，信息保存在 tc_dic
'''
def getRouterTC(tc_dic, content):
    confInfo = yaml.load(content, Loader=yaml.SafeLoader)
    for key, value in confInfo.items():
        ip = value['ip']
        password = value['password']
        # 登录路由器
        tc = TC(ip, password)
        tc.login()
        tc_dic[key] = tc

'''
功能：根据CIDR格式的IP信息，解析出端口Ip和子网掩码
输入：CIDR格式的IP信息，如：172.16.1.1/24
输出：端口ip(172.16.1.1)、子网掩码(255.255.255.0)
'''
def getPortIpAndNetmask(portIPNet):
    host = ipaddress.ip_interface(portIPNet)
    portIP = str(host.ip)
    netmask = host.netmask
    return portIP, netmask

'''
根据配置信息，搭建网络拓扑
输入：路由器的tc客户端(tc_dic)，配置文件内容(content)
输出：拓扑搭建结果
'''
def buildTopology(tc_dic, content):
    confInfo = yaml.load(content, Loader=yaml.SafeLoader)
    for key, value in confInfo.items():
        print(key)
        ports = value['port']
        commands = value['command']

        # 设置路由器各个端口Ip
        tc = tc_dic[key]
        tc.exec_cmd('conf t')
        for p in ports:
            portName = list(p.keys())[0]
            portIPNet = p[portName]
            # 分别获取端口Ip和掩码
            portIP, netmask = getPortIpAndNetmask(portIPNet)
            # 设置端口ip
            tc.setPortIp(portName, portIP, netmask)
        # 执行命令
        for c in commands:
            tc.exec_cmd(c)

        # 查看配置信息
        tc.exec_cmd('end')
        tc.exec_cmd('show ip route')
        print(key, ' conf success!')

'''
功能：更新路由器端口信息
输入：tc, portInfo = {'router': 'RouterA', 'portName': 's0/0/0', 'portIPNet': '172.16.1.1/24', 'status': 'up'}
输出：更新结果(True|False)
'''
def updatePortInfo(tc, portInfo):
    portName = portInfo['portName']
    portIP, netmask = getPortIpAndNetmask(portInfo['portIP'])
    status = portInfo['status']
    net = cal_portNetIp(portInfo['portIP'])
    portInfo['portNet'] = net

    tc.exec_cmd('conf t')
    if status == 'down':
        tc.exec_cmd('int %s' % portName)
        tc.exec_cmd('shutdown')
    else:
        tc.setPortIp(portName, portIP, netmask)

    return portInfo

'''
功能：一键清空当前配置
输入：路由器的tc客户端(tc_dic)，配置文件内容(content)
输出：配置结果
'''
def clearConfiguration(tc_dic, content):
    confInfo = yaml.load(content, Loader=yaml.SafeLoader)
    for key, value in confInfo.items():
        print(key)
        ports = value['port']
        commands = value['command']

        # 清空路由器各个端口Ip，仅保留 f0/0，因为 telnet连接需要用到
        tc = tc_dic[key]
        tc.exec_cmd('conf t')
        for p in ports:
            portName = list(p.keys())[0]
            # 保留 f0/0端口，因为 telnet是通过 f0/0与路由器建立链接
            if portName == 'f0/0':
                continue
            # 对于环回端口，采用 no命令；对于其他端口，采用 default命令
            if portName[0].upper() == 'L':
                tc.exec_cmd('no int %s' % portName)
            else:
                tc.exec_cmd('default int %s' % portName)

        # 清空路由表
        for c in commands:
            if c.startswith('ip route'):
                tc.exec_cmd('no %s' % c)
            elif c == 'router rip' or c == 'router ospf 1':
                tc.exec_cmd('no %s' % c)
                break

        # 查看配置信息
        tc.exec_cmd('end')
        tc.exec_cmd('show running-config')
        print(key, ' clear success!')

'''
功能：根据配置文件内容，测试拓扑的正确性
输入：路由器的tc客户端(tc_dic)，测试文件内容(content)
输出：用例执行结果
'''
def verifyTopology(tc_dic, content):
    caseInfo = json.loads(content)
    for key, value in caseInfo.items():
        router = value['router']
        input = value['input']
        exp_output = value['output']
        tc = tc_dic.get(router)

        print('expected output\n-------------', exp_output)
        print('real output\n------------')
        real_output = tc.exec_cmd(input)
        if exp_output == real_output:
            print(router, key, ' pass!')
        else:
            print(router, key, ' fail!')

# filePath = 'static/conf.yml'
# with open(filePath, 'r') as f:
#     content = f.read()
#     # routerInfo = getRouterInfo(content)
#     # connectionInfo = getConnectionInfo(routerInfo)
#     # print(routerInfo)
#     # print(connectionInfo)
#     buildTopology(content)





