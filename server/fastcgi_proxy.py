import os
from subprocess import check_output, STDOUT
from subprocess import CalledProcessError, TimeoutExpired

from server.serpro import SerPro


class FastCGIProxy(SerPro):
    def __init__(self):
        super().__init__(self.__class__.__name__)
        self.conlen_env = 'CONTENT_LENGTH'
        self.env_key_map = {
            'QUERY_STRING': '',
            'HTTP_COOKIE': 'Cookie',
            'CONTENT_TYPE': 'Content-Type',
            self.conlen_env: self.conlen_key,
        }


    def putenv(self, key, val):
        os.putenv(key, val)
        self.log(f'{key}\n{val}', 'PUT ENV')


    def dispatch(self, method, path, content, header):
        self.putenv('REQUEST_METHOD', method)
        self.putenv('SCRIPT_FILENAME', self.docroot + path)
        for env, key in self.env_key_map.items():
            if key in header:
                self.putenv(env, header[key])

        if content:
            conlen = str(len(content))
            if method == 'GET':
                # GET requests - Ignoring 'Con-Len' header:
                # Set query string to environment variable
                self.putenv('QUERY_STRING', content)
                content = ''
            elif self.conlen_key in header:
                # Non-GET requests - With 'Con-Len' header:
                # 'Con-Len' is asserted to be equal with conlen
                if header[self.conlen_key] != conlen:
                    return self.encode(self.http_resp(500))
            else:
                # Non-GET requests - Without 'Con-Len' header:
                # Set the 'Con-Len' environment variable
                self.putenv(self.conlen_env, conlen)

        shell_exec = 'cgi-fcgi -bind -connect ' + self.fastcgi['upstream']
        try:
            shell_ret = check_output(
                shell_exec,
                shell = True,
                input = content,
                stderr = STDOUT,
                timeout = self.fastcgi['timeout'],
            )
            self.log(shell_ret, 'SHELL RET', self.logc['szth'])
        except CalledProcessError as err:
            if err.returncode == 11:
                return self.encode(self.http_resp(413))
            return self.encode(self.http_resp(502))
        except TimeoutExpired:
            return self.encode(self.http_resp(504))

        # Unset optional envs to prevent pollution in next run
        [os.unsetenv(env) for env in self.env_key_map.keys()]

        resp = self.encode(self.http_resp())
        resp += shell_ret
        return resp


if __name__ == '__main__':
    payloads = [
        [
            ('GET', '/forum/showMsg.php', '', {}),
            (
                'POST', '/forum/leaveMsg.php',
                'captcha=Yatpd&nickname=董先生&message=吼蛙'.encode('utf-8'),
                {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Cookie': 'PHPSESSID=5ol9v510qkem1hd8kg4s5r3vsi; path=/',
                },
            ),
            ('GET', '/forum/showMsg.php', '', {}),
        ],
        [
            ('GET', '/assets/captcha/captcha.php', '', {}),
        ],
    ]

    fcp = FastCGIProxy()
    for argv in payloads[0]:
        print(fcp.decode(fcp.dispatch(*argv)))
    for argv in payloads[1]:
        print(fcp.dispatch(*argv))
