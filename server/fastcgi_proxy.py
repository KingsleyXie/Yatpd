import os
from subprocess import check_output, STDOUT

from server.sp import SP
from log.log import Log


class FastCGIProxy(SP):
    def __init__(
        self,
        root_dir,
        proj_name='',
        sock_dir='/run/php/php7.2-fpm.sock',
        **kwargs):
        super().__init__(root_dir=root_dir, proj_name=proj_name)
        self.sock_dir = sock_dir
        self.optional_env_list = [
            'HTTP_COOKIE',
            'QUERY_STRING',
            'CONTENT_LENGTH',
            'CONTENT_TYPE'
        ]
        self.log = Log('FastCGIProxy', self.conf['logfile']).append


    def putenv(self, key, val):
        os.putenv(key, val)
        self.log(f'{key}\n{val}', 'PUT ENV')


    def dispatch(self, method, path, content=None, header={}):
        self.putenv('REQUEST_METHOD', method)
        self.putenv('SCRIPT_FILENAME', f'{self.root_dir}{path}')
        if 'Cookie' in header:
            self.putenv('HTTP_COOKIE', header['Cookie'])

        shell_input = None
        if content:
            if method == 'GET':
                self.putenv('QUERY_STRING', content)
            else:
                shell_input = content
                self.putenv('CONTENT_LENGTH', str(len(shell_input)))
                if 'Content-Type' in header:
                    self.putenv('CONTENT_TYPE', header['Content-Type'])

        status_ok = self.status['ok']
        resp = f'{self.httpver} {status_ok}{self.CRLF}'
        resp += f'{self.ser_info}{self.CRLF}'
        resp = self.encode(resp)

        shell_ret = check_output(
            f'cgi-fcgi -bind -connect {self.sock_dir}',
            input=content,
            shell=True,
            stderr=STDOUT
        )
        self.log(shell_ret, 'SHELL RET')
        resp += shell_ret

        # Unset optional envs to prevent pollution in next run
        [os.unsetenv(env) for env in self.optional_env_list]

        return resp


if __name__ == '__main__':
    payloads = [
        [
            ('GET', '/forum/showMsg.php'),
            (
                'POST', '/forum/leaveMsg.php',
                'captcha=Yatpd&nickname=董先生&message=吼蛙'.encode('utf-8'),
                {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Cookie': 'PHPSESSID=5ol9v510qkem1hd8kg4s5r3vsi; path=/'
                }
            ),
            ('GET', '/forum/showMsg.php')
        ],
        [
            ('GET', '/assets/captcha/captcha.php'),
        ]
    ]

    from config.config import getconf
    conf = getconf()
    fcp = FastCGIProxy(conf['docroot'], conf['project'], conf['sockfile'])
    for argv in payloads[0]:
        print(fcp.decode(fcp.dispatch(*argv)))
    for argv in payloads[1]:
        print(fcp.dispatch(*argv))
