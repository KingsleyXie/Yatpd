import requests

class HttpProxy:
    def __init__(self, site):
        self.site = site
        self.EOL = '\r\n'

    def _convert_bin_ret(self, res):
        raw_res = res.raw
        status_line = f'HTTP/{raw_res.version // 10}.{raw_res.version % 10} '
        status_line += f'{raw_res.status} {raw_res.reason}{self.EOL}'
        response_header = self.EOL.join(f'{k}: {v}' for k, v in raw_res.headers.items())
        ret = bytes(f'{status_line}{response_header}{self.EOL * 2}', 'utf-8')
        ret += raw_res.data
        return ret

    def get(self, path, params=None):
        return self._convert_bin_ret(
            requests.get(f'{self.site}{path}', params=params, stream=True)
        )

    def post(self, path, data=None):
        return self._convert_bin_ret(
            requests.post(f'{self.site}{path}', data=data, stream=True)
        )

    def put(self, path, data=None):
        return self._convert_bin_ret(
            requests.put(f'{self.site}{path}', data=data, stream=True)
        )

    def delete(self, path):
        return self._convert_bin_ret(
            requests.delete(f'{self.site}{path}', stream=True)
        )


if __name__ == '__main__':
    hp = HttpProxy('https://httpbin.org')
    print(hp.get('/status/200'))
    print(hp.get('/get', params = {'key': 'value'}))
    print(hp.post('/post', data = {'key': 'value'}))
    print(hp.put('/put', data = {'key': 'value'}))
    print(hp.delete('/delete'))
