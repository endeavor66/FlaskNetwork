import yaml
from flask import Flask, render_template, redirect, abort, request, jsonify
from service import getRouterInfo, getConnectionInfo, getRouterTC, buildTopology, updatePortInfo, clearConfiguration, verifyTopology, closeRouter
from myTelnetClient import TelnetClient as TC

app = Flask(__name__)

# routerInfo = [
#     {
#         'name': 'RouterA',
#         'ports': [
#             {
#                 'name': 's0/0/0',
#                 'ip': '172.16.1.1',
#                 'status': 'up'
#             },
#             {
#                 'name': 's0/0/1',
#                 'ip': 'unassigned',
#                 'status': 'down'
#             }
#         ]
#     },
#     {
#         'name': 'RouterB',
#         'ports': [
#             {
#                 'name': 's0/0/0',
#                 'ip': '172.16.1.2',
#                 'status': 'up'
#             },
#             {
#                 'name': 's0/0/1',
#                 'ip': '172.16.2.1',
#                 'status': 'up'
#             }
#         ]
#     },
#     {
#         'name': 'RouterC',
#         'ports': [
#             {
#                 'name': 's0/0/0',
#                 'ip': '172.16.2.2',
#                 'status': 'up'
#             },
#             {
#                 'name': 's0/0/1',
#                 'ip': 'unassigned',
#                 'status': 'down'
#             }
#         ]
#     }
# ]

# connection = [
#     {
#       "from": {
#         "name": "RouterA",
#         "port": "s0/0/0",
#         "portIP": "192.168.1.2"
#       },
#       "to": {
#         "name": "RouterB",
#         "port": "s0/0/0",
#         "portIP": "192.168.1.1"
#       }
#     },
#
#     {
#       "from": {
#         "name": "RouterB",
#         "port": "s0/0/1",
#         "portIP": "192.168.2.1"
#       },
#       "to": {
#         "name": "RouterC",
#         "port": "s0/0/0",
#         "portIP": "192.168.2.2"
#       }
#     }
# ]

# 记录每个路由器的交互端，格式：{routerName: telnetClient}。避免反复登录/退出路由器
tc_dic = {}

# 记录配置文件内容
conf_content = ''

@app.route('/')
def index():
    return render_template('combine.html')

'''
功能：根据前端传过来的文件名，读取文件内容并返回
接受：文件名
返回：文件内容
'''
@app.route('/file', methods=('GET', 'POST'))
def file_read():
    fileName = request.form["fileName"]
    filePath = 'static/' + fileName
    with open(filePath) as reader:
        content = reader.read()
        return content

'''
功能：根据前端传过来的文件内容，搭建网络拓扑，返回拓扑信息。同时将各路由器的连接类记录在 tc_dic 中
接受：文件内容
返回：拓扑信息，包含：路由器端口信息、链路信息
'''
@app.route("/send", methods=('GET', 'POST'))
def send():
    global tc_dic
    global conf_content
    conf_content = yaml.load(request.form['content'], Loader=yaml.SafeLoader)
    # 获取路由器端口信息，格式见 routerInfo
    routerInfo = getRouterInfo(conf_content)
    # 识别网络拓扑关系，格式见 connection
    connection = getConnectionInfo(routerInfo)
    print(routerInfo)
    print(connection)
    # 获取每个路由器的Telnet客户端
    getRouterTC(tc_dic, conf_content)
    # 根据conf_content内容搭建网络拓扑
    # buildTopology(tc_dic, conf_content)
    return jsonify({"routerInfo": routerInfo, "connection": connection})

'''
功能：根据前端传过来的命令，让特定路由器执行
接受：命令
返回：命令执行结果
'''
@app.route("/execute", methods=('GET', 'POST'))
def execute():
    global tc_dic
    routerName = request.form['router']
    cmd = request.form['command']
    print(routerName)
    print(cmd)
    # 路由器执行命令，返回结果
    tc = tc_dic.get(routerName)
    res = tc.exec_cmd(cmd)
    # res 裁剪首尾行（首行：输入的命令；尾行：输入提示符）
    res = '\n'.join(res.split('\n')[1:-1])
    return res

'''
功能：根据测试文件校验拓扑的正确性
接受：测试文件内容
返回：拓扑各个case校验结果
'''
@app.route("/topologyTest", methods=('GET', 'POST'))
def topologyTest():
    global tc_dic
    content = request.form['content']
    res = verifyTopology(tc_dic, content)
    # res = {'case1': 'pass', 'case2': 'pass','case3': 'fail','case4': 'pass'}
    return res

'''
功能：更新路由端口信息
接受：新的路由端口信息，格式：{router: RouterA, portName: s0/0/0, portIPNet: 172.16.1.1/24, status: up}
返回：更新结果(True|False)
'''
@app.route("/update", methods=('GET', 'POST'))
def updatePort():
    global tc_dic
    # portInfo = {'router': 'RouterA', 'portName': 's0/0/0', 'portIP': '172.16.1.1/24', 'status': 'up'}
    global conf_content
    portInfo = dict(request.form)
    router = portInfo['router']
    tc = tc_dic[router]
    newPortInfo = updatePortInfo(tc, portInfo, conf_content)
    return jsonify({"newPortInfo": newPortInfo, "conf_content": yaml.dump(conf_content)})

'''
功能：一键清空当前配置
接受：清空请求
返回：操作结果(True|False)
'''
@app.route("/clear", methods=['GET'])
def clearConf():
    global tc_dic
    global conf_content
    clearConfiguration(tc_dic, conf_content)
    return 'success'

if __name__ == '__main__':
    app.run(debug=True)
