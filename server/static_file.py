import re
import os.path as ospath
from urllib.parse import unquote

from server.serpro import SerPro


class StaticFile(SerPro):
    def __init__(self):
        super().__init__(self.__class__.__name__)


    def dispatch(self, method, path, content, header):
        return self.get(method, path)


    def get(self, method, path):
        if not ospath.isfile(f'{self.docroot}{path}'):
            if '.' not in path and path[-1] != '/':
                # Redirect with `/`
                loct = f'{path}/'
                self.log(
                    f'Redirecting Path `{path}` To `{loct}`',
                    'PREPARE PATH'
                )
                return self.encode(self.resp_gen(303, loct=loct))
            elif path[-1] == '/':
                # Add index file to path
                self.log(
                    f'Adding Index File To Path:\n{path}',
                    'PREPARE PATH'
                )
                path += self.idxfile

        try:
            abs_path = unquote(f'{self.docroot}{path}')
            f = open(abs_path, 'rb')
            file_content = f.read()
            self.log(
                f'File Content Got, Closing File:\n{abs_path}',
                'FILE OPEN'
            )
            f.close()
        except IOError:
            # File not found
            self.log(f'File Not Found:\n{abs_path}', 'FILE OPEN')
            return self.encode(self.resp_gen(404))

        content_type = self.mime_type_default
        for regex, mtype in self.mime_type_map.items():
            if re.search(regex, path):
                content_type = mtype
                self.log(
                    f'Path `{path}`\nUsing Regex `{regex}`\nMatched MIME Type `{mtype}`',
                    'MIME TYPE'
                )
                break

        resp = self.resp_gen(200, False)
        resp += f'Content-Type: {content_type}{self.CRLF}'
        resp += f'Content-Length: {len(file_content)}{self.CRLF}'
        resp += self.CRLF
        self.log(resp, 'RESP HEAD')

        resp = self.encode(resp)
        resp += file_content
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
            ('POST', '/', '', {}),
            ('GET', '/initDB.sql', '', {}),
            ('GET', '/assets/js/competition.js', '', {}),
            ('GET', '/assets/css/competition.css', '', {}),
        ],
        [
            ('GET', '/assets/pictures/icon.png', '', {}),
            ('GET', '/assets/font/elephant.ttf', '', {}),
        ]
    ]

    sf = StaticFile()
    for argv in payloads[0]:
        print(sf.decode(sf.dispatch(*argv)))
    for argv in payloads[1]:
        print(sf.dispatch(*argv))
