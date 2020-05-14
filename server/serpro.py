# Server/Proxy Base Class

import os.path as ospath

from log.log import Log
from config import config


class SerPro:
    def __init__(self, component):
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


    # Check if a given file path exists
    def file_exists(self, path):
        if not ospath.isfile(path):
            self.log(f'File Not Found: {path}', 'FILE OPEN')
            return False
        return True


    # Get binary file content with given path
    def file_content(self, path, once=False):
        try:
            f = open(path, 'rb')
            content = f.read()
            self.log(
                f'File Content Got, Closing File: {path}',
                'FILE OPEN'
            )
            f.close()
        except Exception:
            self.log(f'File Open Failed: {path}', 'FILE OPEN')
            content = b'' if once \
                else self.http_resp(500)
        return content


    # Generate HTTP response according to status code
    def http_resp(self, status=200, location=None):
        ranges = {
            'success': range(200, 300),
            'redirect': range(300, 400),
            'error': range(400, 600)
        }

        if status in ranges['redirect'] and not location:
            status = 500

        use_errpage = False
        if status in ranges['error'] and status in self.errpage['file']:
            errfile = self.errpage['docroot'] + self.errpage['file'][status]
            if self.file_exists(errfile):
                use_errpage =  True
                file_binary = self.file_content(errfile, True)
            else:
                self.log(
                    f'Error Page File Not Found For Status {status}',
                    'HTTP RESP GEN'
                )

        resp = f'{self.httpver} {self.status[status]}{self.CRLF}'
        resp += f'Server: {self.project}{self.CRLF}'
        resp += f'Location: {location}{self.CRLF}' if location else ''
        resp += self.errpage['header'] + self.CRLF if use_errpage else ''

        if status not in ranges['success']:
            if use_errpage:
                resp += f'{self.conlen_key}: {len(file_binary)}{self.CRLF}'

            resp += self.CRLF
            resp = self.encode(resp)

            if use_errpage:
                resp += file_binary

        self.log(resp, 'HTTP RESP GEN', self.logc['small'], False)
        return resp
