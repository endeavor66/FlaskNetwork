import yaml

filePath = 'static/conf.yml'

if filePath.startswith('static'):
    print(True)
else:
    print(False)