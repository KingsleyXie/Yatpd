import os
from subprocess import getoutput

from sp import SP


class FastCGIProxy(SP):
    def __init__(self, root_dir, proj_name='', sock_dir='/run/php/php7.2-fpm.sock'):
        super().__init__(root_dir=root_dir, proj_name=proj_name)
        self.sock_dir = sock_dir
        self.optional_env_list = [
            'HTTP_COOKIE',
            'QUERY_STRING',
            'CONTENT_LENGTH',
            'CONTENT_TYPE'
        ]


    def _escape_quotes(self, content):
        content = content.replace('"', '\\"')
        content = content.replace('\'', '\\\'')
        return content


    def dispatch(self, method, path, content=None, header={}):
        os.putenv('REQUEST_METHOD', method)
        os.putenv('SCRIPT_FILENAME', f'{self.root_dir}{path}')
        if 'Cookie' in header:
            os.putenv('HTTP_COOKIE', header['Cookie'])

        # Two types of commands depending on whether stdin is needed:
        # $ /bin/bash -c "cgi-fcgi -bind -connect /run/php/php7.2-fpm.sock"
        # $ /bin/bash -c "cgi-fcgi -bind -connect /run/php/php7.2-fpm.sock <<< 'foo=bar&key=val'"
        cmd = '/bin/bash -c "cgi-fcgi -bind -connect ' + self.sock_dir
        if content:
            if method == 'GET':
                os.putenv('QUERY_STRING', content)
            else:
                cmd += ' <<< \'' + self._escape_quotes(content) + '\''
                os.putenv('CONTENT_LENGTH', str(len(bytes(content, 'utf-8'))))
                if 'Content-Type' in header:
                    os.putenv('CONTENT_TYPE', header['Content-Type'])
        cmd += '"'
        print(f'$ {cmd}')

        status_ok = self.status_table['ok']
        ret = f'{self.http_version} {status_ok}\n{self.server_info}\n'
        ret += getoutput(cmd)

        # Unset optional envs to prevent pollution in next run
        [os.unsetenv(env) for env in self.optional_env_list]

        ret = ret.replace('\n', self.EOL)
        return bytes(ret, 'utf-8')
