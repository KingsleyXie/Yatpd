# Server/Proxy Base Class

class SP(object):
    def __init__(self, root_dir='', proj_name='', encoding='utf-8'):
        super().__init__()

        self.EOL = '\r\n'
        self.root_dir = root_dir
        self.encoding = encoding
        self.http_version = 'HTTP/1.1'
        self.server_info = f'Server: {proj_name}'

        # HTTP status code in use
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
        self.status_table = {
            'ok': '200 OK',
            'nf': '404 Not Found',
            'na': '405 Method Not Allowed'
        }
