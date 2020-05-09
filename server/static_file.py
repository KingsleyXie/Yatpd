import re
import os.path as ospath
from urllib.parse import unquote

from server.sp import SP
from log.log import Log


class StaticFile(SP):
    def __init__(
        self,
        root_dir,
        proj_name='',
        index_file='index.html',
        **kwargs):
        super().__init__(root_dir=root_dir, proj_name=proj_name)
        self.index_file = index_file
        self.log = Log('StaticFile', self.conf['logfile']).append


    def gen_resp(self, status, end=True, redirect=None):
        resp = f'{self.httpver} {status}{self.CRLF}'
        resp += f'{self.ser_info}{self.CRLF}'
        resp += f'Location: {redirect}' if redirect else ''
        resp += self.CRLF if end else ''
        self.log(resp, 'RESP GEN')
        return resp


    def dispatch(self, method, path, content=None, header={}):
        if method not in self.conf['sf_allow_methods']:
            return self.encode(
                self.gen_resp(self.status['na'])
            )
        else:
            if not ospath.isfile(f'{self.root_dir}{path}'):
                if '.' not in path and path[-1] != '/':
                    # Redirect with `/`
                    redirect = f'{path}/'
                    self.log(
                        f'Redirecting Path `{path}` To `{redirect}`',
                        'PREPARE PATH'
                    )
                    return self.encode(
                        self.gen_resp(self.status['so'], redirect=redirect)
                    )
                elif path[-1] == '/':
                    # Add index file to path
                    self.log(
                        f'Adding Index File To Path:\n{path}',
                        'PREPARE PATH'
                    )
                    path += self.index_file
            try:
                abs_path = unquote(f'{self.root_dir}{path}')
                f = open(abs_path, 'rb')
                file_content = f.read()
                f.close()
                self.log(
                    f'Got File Content And Closed File:\n{abs_path}',
                    'FILE OPEN'
                )
            except IOError:
                # File not found
                self.log(f'File Not Found:\n{abs_path}', 'FILE OPEN')
                return self.encode(
                    self.gen_resp(self.status['nf'])
                )

        content_type = self.conf['mime_type_default']
        for regex, mtype in self.conf['mime_type_map'].items():
            if re.search(regex, path):
                content_type = mtype
                self.log(
                    f'Path `{path}`\nUsing Regex `{regex}`\nMatched MIME Type `{mtype}`',
                    'MIME TYPE'
                )
                break
        resp = self.gen_resp(self.status['ok'], False)
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
            ('GET', '/'),
            ('GET', '/forum'),
            ('GET', '/forum/'),
            ('GET', '/wrong/path.ext'),
            ('GET', '/wrong/path'),
            ('GET', '/wrong/path/'),
            ('POST', '/'),
            ('GET', '/initDB.sql'),
            ('GET', '/assets/js/competition.js'),
            ('GET', '/assets/css/competition.css'),
        ],
        [
            ('GET', '/assets/pictures/icon.png'),
            ('GET', '/assets/font/elephant.ttf'),
        ]
    ]

    from config.config import getconf
    conf = getconf()
    sf = StaticFile(conf['docroot'], conf['project'], conf['idxfile'])
    for argv in payloads[0]:
        print(sf.decode(sf.dispatch(*argv)))
    for argv in payloads[1]:
        print(sf.dispatch(*argv))
