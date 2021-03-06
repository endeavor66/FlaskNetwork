import re
import yaml

# extract_ping
# info = "\nType escape sequence to abort.\nSending 5, 100-byte ICMP Echos to 10.0.0.1, timeout is 2 seconds:\n!!!!!\nSuccess rate is 0 percent (5/5), round-trip min/avg/max = 31/34/47 ms"
# searchObj = re.search( r'Success rate is \d+ percent', s)
# if searchObj:
#    print(searchObj.group())

# extract_LSA
# info = "            OSPF Router with ID (192.168.4.1) (Process ID 1)\n\n                Router Link States (Area 0)\n\nLink ID         ADV Router      Age         Seq#       Checksum Link count\n192.168.4.1     192.168.4.1     655         0x80000003 0x0069e6 2\n172.16.3.1      172.16.3.1      655         0x80000003 0x008a72 2\n\n                Summary Net Link States (Area 0)\nLink ID         ADV Router      Age         Seq#       Checksum\n172.16.1.1      172.16.3.1      661         0x80000001 0x004b93\n172.16.2.1      172.16.3.1      661         0x80000002 0x003e9e\n172.16.3.1      172.16.3.1      661         0x80000003 0x0031a9\n192.168.4.0     192.168.4.1     616         0x80000001 0x0087fa\n\n                Router Link States (Area 51)\n\nLink ID         ADV Router      Age         Seq#       Checksum Link count\n192.168.4.1     192.168.4.1     621         0x80000002 0x000297 1\n172.24.2.1      172.24.2.1      621         0x80000002 0x0036b0 1\n\n                Net Link States (Area 51)\nLink ID         ADV Router      Age         Seq#       Checksum\n192.168.4.1     192.168.4.1     621         0x80000001 0x006c62\n\n                Summary Net Link States (Area 51)\nLink ID         ADV Router      Age         Seq#       Checksum\n192.168.1.0     192.168.4.1     616         0x80000001 0x002125\n172.16.1.1      192.168.4.1     616         0x80000002 0x004ba4\n172.16.2.1      192.168.4.1     616         0x80000003 0x003eaf\n172.16.3.1      192.168.4.1     616         0x80000004 0x0031ba"
# pattern = re.compile(r'Router Link States \(Area \w+\)|Summary Net Link States \(Area \w+\)|Net Link States \(Area \w+\)')
# res = pattern.findall(info)
# res.sort()
# print(res)

# extract_route
info = "Codes: C - connected, S - static, I - IGRP, R - RIP, M - mobile, B - BGP\n       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area\n       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2\n       E1 - OSPF external type 1, E2 - OSPF external type 2, E - EGP\n       i - IS-IS, L1 - IS-IS level-1, L2 - IS-IS level-2, ia - IS-IS inter area\n       * - candidate default, U - per-user static route, o - ODR\n       P - periodic downloaded static route\n\nGateway of last resort is not set\n\n     172.16.0.0/24 is subnetted, 3 subnets\nC       172.16.1.0 is directly connected, Loopback0\nC       172.16.2.0 is directly connected, Loopback1\nC       172.16.3.0 is directly connected, Loopback2\nR    10.0.0.0/8 [120/1] via 192.168.2.2, 00:00:04, Serial0/0/1\nC    192.168.1.0/24 is directly connected, Serial0/0/0\nO IA 192.168.4.0/24 [110/65] via 192.168.1.1, 00:14:14, Serial0/0/0"
pattern = re.compile(r'((C|S|R|O IA)\s+\d+\.\d+\.\d+\.\d+)')
res = [p[0] for p in pattern.findall(info)]
res.sort()
print(res)
# with open('static/conf_staticRoute.yml') as reader:
#     content = reader.read()
#     confInfo = yaml.load(content, yaml.SafeLoader)
#     for p in confInfo['RouterA']['port']:
#         if list(p.keys())[0] == 's0/0/0':
#             print(p)