from app import root_url

def enroute(path):
    return '{}{}'.format(root_url, path)
