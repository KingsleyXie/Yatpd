# Server/Proxy Base Class

from log.log import Log
from config import config


class SerPro(object):
    def __init__(self, component):
        super().__init__()

        for key, val in config.get().items():
            setattr(self, key, val)

        self.log = Log(component, self.logc['file']).append

        self.CRLF = '\r\n'
        self.conlen_key = 'Content-Length'


    # None-able content encode with configured encoding
    def encode(self, content):
        if content:
            return content.encode(self.contenc)
        return None


    # None-able content decode with configured encoding
    def decode(self, content):
        if content:
            return content.decode(self.contenc)
        return None


    # Generate HTTP responses according to status code
    def http_resp(self, status=200, end=True, loct=None):
        end = False if status == 200 else end
        if status in range(300, 400) and not loct:
            status = 500

        status = self.status[status]
        resp = f'{self.httpver} {status}{self.CRLF}'
        resp += f'Server: {self.project}{self.CRLF}'
        resp += f'Location: {loct}' if loct else ''
        resp += self.CRLF if end else ''
        self.log(resp, 'HTTP RESP')
        return resp
