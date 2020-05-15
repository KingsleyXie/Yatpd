import os
from subprocess import TimeoutExpired
from subprocess import run, STDOUT, PIPE

from server.serpro import SerPro
from server.mocker import mock_request


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


    def dispatch(self, method, path, query, content, header):
        scriptfile = self.fastcgi['docroot'] + path
        if not self.file_exists(scriptfile):
            return self.http_resp(404)

        self.putenv('QUERY_STRING', query)
        self.putenv('REQUEST_METHOD', method)
        self.putenv('SCRIPT_FILENAME', scriptfile)
        for env, key in self.env_key_map.items():
            if key in header:
                self.putenv(env, header[key])

        cmd = 'cgi-fcgi -bind -connect ' + self.fastcgi['upstream']
        try:
            cmd_ret = run(
                cmd,
                input = content,
                stderr = STDOUT,
                stdout = PIPE,
                shell = True,
                timeout = self.fastcgi['timeout'],
            )
        except TimeoutExpired:
            return self.http_resp(504)

        # Unset optional envs to prevent pollution in next run
        [os.unsetenv(env) for env in self.env_key_map.keys()]

        retcode, retcont = cmd_ret.returncode, cmd_ret.stdout
        self.log(str(retcode), 'CMD RETCODE')
        self.log(retcont, 'CMD RETCONT', self.logc['large'], False)
        if retcode:
            retcode_status_map = {
                # Possible reason: large content sent to WSL Unix socket
                11: 413,
                # Could not connect to upstream
                111: 503
            }
            if retcode in retcode_status_map:
                return self.http_resp(retcode_status_map[retcode])
            return self.http_resp(502)

        # Parse entity body of command returned data to calculate length
        double_crlf = self.encode(self.CRLF * 2)
        retbody = retcont if double_crlf not in retcont \
            else retcont.split(double_crlf, 1)[1]

        # Add Content-Length header to the response
        resp_header = self.http_resp()
        resp_header += f'{self.conlen_key}: {len(retbody)}{self.CRLF}'

        # Generate actual response binary data
        resp = self.encode(resp_header)
        resp += retcont
        return resp


if __name__ == '__main__':
    payloads = {
        'text': [
            ['GET', '/forum/showMsg.php'],
            [
                'POST', '/forum/leaveMsg.php', '',
                'captcha=Yatpd&nickname=董先生&message=吼蛙'.encode('utf-8'),
                {
                    'Content-Length': '47',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Cookie': 'PHPSESSID=5l1b95t2oqmtiqiffivp1phet0; path=/',
                },
            ],
            ['GET', '/forum/showMsg.php'],
        ],
        'raw': [
            ['GET', '/assets/captcha/captcha.php'],
        ],
    }
    mock_request(payloads, FastCGIProxy())
