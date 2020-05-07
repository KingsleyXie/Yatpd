import re
import os
import sys

class StaticFile:
    def __init__(self, root_dir, project_name, index_file='/index.html'):
        self.root_dir = root_dir
        self.index_file = index_file

        self.EOL = '\r\n'
        self.http_version = 'HTTP/1.1'
        self.server_info = f'Server: {project_name}{self.EOL}'

        # HTTP status code in use
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
        self.status_ok = '200 OK'
        self.status_not_found = '404 Not Found'

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


    def get(self, path):
        path = self.index_file if path == '/' else path
        try:
            static_file = open(self.root_dir + path, 'rb')
        except FileNotFoundError:
            status = self.status_not_found
        else:
            status = self.status_ok
            file_content = static_file.read()
            static_file.close()
        response = f'{self.http_version} {status}{self.EOL}'
        response += f'{self.server_info}'
        if status == self.status_not_found:
            return bytes(response, 'utf-8')

        content_type = self.default_mime
        for regex, mime_type in self.ext_mime_map.items():
            if re.search(regex, path):
                content_type = mime_type
        response += f'Content-Type: {content_type}{self.EOL}'
        response += f'Content-Length: {len(bytes(file_content))}{self.EOL}'
        response += self.EOL
        response = bytes(response, 'utf-8')
        response += file_content
        return response
