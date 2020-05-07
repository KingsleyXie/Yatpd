import requests

from sp import SP

class HttpProxy(SP):
    def __init__(self, site):
        super().__init__()
        self.site = site

    def _convert_bin_ret(self, res):
        raw_res = res.raw
        status_line = f'HTTP/{raw_res.version // 10}.{raw_res.version % 10} '
        status_line += f'{raw_res.status} {raw_res.reason}{self.EOL}'
        response_header = self.EOL.join(f'{k}: {v}' for k, v in raw_res.headers.items())
        ret = bytes(f'{status_line}{response_header}{self.EOL * 2}', 'utf-8')
        ret += raw_res.data
        return ret

    def dispatch(self, method, path, content=None, header={}):
        data_key = 'params' if method == 'GET' else 'data'
        return self._convert_bin_ret(
            getattr(requests, method.lower())(**{
                'url': f'{self.site}{path}',
                'stream': True,
                data_key: content
            })
        )


if __name__ == '__main__':
    hp = HttpProxy('https://httpbin.org')
    print(hp.dispatch('GET', '/status/200'))
    print(hp.dispatch('GET', '/get', {'key': 'value'}))
    print(hp.dispatch('POST', '/post', {'key': 'value'}))
    print(hp.dispatch('PUT', '/put', {'key': 'value'}))
    print(hp.dispatch('DELETE', '/delete'))
