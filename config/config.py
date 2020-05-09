import yaml

def getconf(filename='config/config.yaml'):
    with open(filename, 'r') as stream:
        data = yaml.safe_load(stream)
    return data
