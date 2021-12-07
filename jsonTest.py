import json
from myTelnetClient import TelnetClient

filePath = 'static/test.json'

with open(filePath, 'r') as f:
    data = json.load(f)
    for key, value in data.items():
        input = value['input']
        exp_output = value['output']

        print(key)
        print(input)
        print(exp_output)
        print()

        # 执行命令
        # tc = TelnetClient()
        # tc.login('172.16.1.1', '', 'CISCO')
        # real_output = tc.exec_cmd('show running-config')
        #
        # # 判断执行结果
        # if real_output == exp_output:
        #     print(key, " pass")
        # else:
        #     print(key, " fail")
            # 分析失败原因，涉及对字符串的解析
