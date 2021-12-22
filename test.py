str = "line1:adkjfg\nline2:ldajfdklafjl\nline3:dafdasf\nline4:dafdafdsa\nline5:dafdadaf"
new_str = '\n'.join(str.split('\n')[1:-1])
print('=====str')
print(str)
print('=====new_str')
print(new_str)