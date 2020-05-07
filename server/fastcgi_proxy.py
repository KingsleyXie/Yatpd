import os

class FastCGIProxy:
    def __init__(self, root_dir, sock_dir='/run/php/php7.2-fpm.sock'):
        self.root_dir = root_dir
        self.sock_dir = sock_dir

    def _escape_quotes(self, content):
        content = content.replace('"', '\\"')
        content = content.replace('\'', '\\\'')
        return content

    def request(self, method, path, header = {}, content = None):
        os.putenv('REQUEST_METHOD', method)
        os.putenv('SCRIPT_FILENAME', f'{self.root_dir}{path}')
        if 'Cookie' in header:
            os.putenv('HTTP_COOKIE', header['Cookie'])

        cmd = '/bin/bash -c ' \
            + '"cgi-fcgi -bind -connect ' \
            + self.sock_dir

        # $ /bin/bash -c "cgi-fcgi -bind -connect /run/php/php7.2-fpm.sock"
        # $ /bin/bash -c "cgi-fcgi -bind -connect /run/php/php7.2-fpm.sock <<< 'foo=bar&key=val'"
        end_cmd = '"'
        if content:
            if method == 'GET':
                os.putenv('QUERY_STRING', content)
            else:
                end_cmd = ' <<< \'' + self._escape_quotes(content) + '\'"'
                os.putenv('CONTENT_LENGTH', str(len(bytes(content, 'utf-8'))))
                if 'Content-Type' in header:
                    os.putenv('CONTENT_TYPE', header['Content-Type'])
        cmd += end_cmd
        print(f'$ {cmd}')
        os.system(cmd)
