import yaml


def get(filename='config/config.yaml'):
    with open(filename, 'r') as stream:
        data = yaml.safe_load(stream)
    return data


if __name__ == '__main__':
    print(get())
