import re
import os
import sys

from sp import SP

class StaticFile(SP):
    def __init__(self, root_dir, index_file='/index.html', proj_name=''):
        super().__init__(root_dir=root_dir, proj_name=proj_name)
        self.index_file = index_file
        self.allowed_methods = ['GET']

        # Map from file extension pattern to HTTP MIME type header
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Type
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types
        self.default_mime = 'text/plain;charset=UTF-8'
        self.ext_mime_map = {
            r'\.html$': 'text/html;charset=UTF-8',
            r'\.js$': 'text/javascript;charset=UTF-8',
            r'\.css$': 'text/css;charset=UTF-8',
            r'\.ttf$': 'font/ttf',
            r'\.woff$': 'font/woff',
            r'\.(jpg|jpeg|jfif|pjpeg|pjp)$': 'image/jpeg',
            r'\.(png)$': 'image/png',
            r'\.(gif)$': 'image/gif',
            r'\.(svg)$': 'image/svg+xml',
            r'\.(webp)$': 'image/webp'
        }


    def dispatch(self, method, path, content=None, header={}):
        if method not in self.allowed_methods:
            status = self.status_table['na']
        else:
            path = self.index_file if path[-1] == '/' else path
            try:
                static_file = open(self.root_dir + path, 'rb')
            except IOError:
                status = self.status_table['nf']
            else:
                status = self.status_table['ok']
                file_content = static_file.read()
                static_file.close()
        ret = f'{self.http_version} {status}{self.EOL}'
        ret += f'{self.server_info}{self.EOL}'
        if status != self.status_table['ok']:
            return bytes(ret, 'utf-8')

        content_type = self.default_mime
        for regex, mime_type in self.ext_mime_map.items():
            if re.search(regex, path):
                content_type = mime_type
        ret += f'Content-Type: {content_type}{self.EOL}'
        ret += f'Content-Length: {len(bytes(file_content))}{self.EOL}'
        ret += self.EOL
        ret = bytes(ret, 'utf-8')
        ret += file_content
        return ret
