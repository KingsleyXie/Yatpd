import re

from server.serpro import SerPro


class StaticFile(SerPro):
    def __init__(self):
        super().__init__(self.__class__.__name__)


    def dispatch(self, method, path, content, header):
        return self.get(method, path)


    def get(self, method, path):
        if not self.file_exists(path):
            if '.' not in path and path[-1] != '/':
                # Redirect with `/`
                location = f'{path}/'
                self.log(
                    f'Redirecting Path `{path}` To `{location}`',
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

        path = self.static['docroot'] + path
        if not self.file_exists(path):
            return self.http_resp(404)
        file_binary = self.file_content(path)

        content_type = self.mime_type_default
        for regex, mtype in self.mime_type_map.items():
            if re.search(regex, path):
                content_type = mtype
                self.log(
                    f'Path `{path}`\n'
                    + f'Using Regex `{regex}`\n'
                    + f'Matched MIME Type `{mtype}`',
                    'MIME TYPE'
                )
                break

        resp = self.http_resp()
        resp += f'Content-Type: {content_type}{self.CRLF}'
        resp += f'Content-Length: {len(file_binary)}{self.CRLF}'
        resp += self.CRLF
        self.log(resp, 'RESP HEAD')

        resp = self.encode(resp)
        resp += file_binary
        return resp


if __name__ == '__main__':
    payloads = [
        [
            ('GET', '/', '', {}),
            ('GET', '/forum', '', {}),
            ('GET', '/forum/', '', {}),
            ('GET', '/wrong/path.ext', '', {}),
            ('GET', '/wrong/path', '', {}),
            ('GET', '/wrong/path/', '', {}),
            ('GET', '/initDB.sql', '', {}),
            ('GET', '/assets/js/competition.js', '', {}),
            ('GET', '/assets/css/competition.css', '', {}),
        ],
        [
            ('GET', '/assets/pictures/icon.png', '', {}),
            ('GET', '/assets/font/elephant.ttf', '', {}),
        ],
    ]

    sf = StaticFile()
    for argv in payloads[0]:
        print(sf.decode(sf.dispatch(*argv)))
    for argv in payloads[1]:
        print(sf.dispatch(*argv))
