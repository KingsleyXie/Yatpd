import re

from server.serpro import SerPro
from server.mocker import mock_request


class StaticFile(SerPro):
    def __init__(self):
        super().__init__(self.__class__.__name__)


    def dispatch(self, method, path, query, content, header):
        return self.get(method, path)


    def get(self, method, path):
        # Check and prepare file path
        file_path = self.static['docroot'] + path
        if not self.file_exists(file_path):
            if '.' not in path and path[-1] != '/':
                # Redirect with /
                location = f'{path}/'
                self.log(
                    f'Redirecting Path {path} To {location}',
                    'PREPARE PATH'
                )
                return self.http_resp(303, location=location)
            elif path[-1] == '/':
                # Add index file to path
                self.log(
                    f'Adding Index File To Path: {path}',
                    'PREPARE PATH'
                )
                path += self.static['idxfile']

        # Get the real file content
        file_path = self.static['docroot'] + path
        if not self.file_exists(file_path):
            return self.http_resp(404)
        file_binary = self.file_content(file_path)

        # Determine MIME type of the file
        content_type = self.mime_type_default
        for regex, mtype in self.mime_type_map.items():
            if re.search(regex, path):
                content_type = mtype
                self.log(
                    f'Path {path}\n'
                    + f'Using Regex {regex}\n'
                    + f'Matched MIME Type {mtype}',
                    'MIME TYPE'
                )
                break

        resp = self.http_resp()
        resp += f'Content-Type: {content_type}{self.CRLF}'
        resp += f'{self.conlen_key}: {len(file_binary)}{self.CRLF}'
        resp += self.CRLF
        self.log(resp, 'RESP HEAD')

        resp = self.encode(resp)
        resp += file_binary
        return resp


if __name__ == '__main__':
    payloads = {
        'text': [
            ['GET'],
            ['GET', '/forum'],
            ['GET', '/forum/'],
            ['GET', '/wrong/path.ext'],
            ['GET', '/wrong/path'],
            ['GET', '/wrong/path/'],
            ['GET', '/initDB.sql'],
            ['GET', '/assets/js/competition.js'],
            ['GET', '/assets/css/competition.css'],
        ],
        'raw': [
            ['GET', '/assets/pictures/icon.png'],
            ['GET', '/assets/font/elephant.ttf'],
        ],
    }
    mock_request(payloads, StaticFile())
