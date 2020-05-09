# Server/Proxy Base Class

from config.config import getconf


class SP(object):
    def __init__(
        self,
        root_dir='',
        proj_name='',
        encoding='utf-8'):
        super().__init__()

        self.conf = getconf()
        self.CRLF = '\r\n'
        self.status = self.conf['status']
        self.bufsize = self.conf['bufsize']
        self.httpver = self.conf['httpver']

        self.root_dir = root_dir
        self.encoding = encoding
        self.ser_info = f'Server: {proj_name}'


    def encode(self, content):
        if content:
            return content.encode(self.encoding)
        return None


    def decode(self, content):
        if content:
            return content.decode(self.encoding)
        return None
