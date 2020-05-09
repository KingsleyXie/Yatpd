import requests
from urllib.parse import parse_qsl

from server.sp import SP
from log.log import Log


class HTTPProxy(SP):
    def __init__(self, http_site, **kwargs):
        super().__init__()
        self.http_site = http_site
        self.log = Log('HTTPProxy', self.conf['logfile']).append


    def _convert_bin_ret(self, res):
        raw_res = res.raw
        status_line = f'HTTP/{raw_res.version // 10}.{raw_res.version % 10} '
        status_line += f'{raw_res.status} {raw_res.reason}{self.CRLF}'
        response_header = self.CRLF.join(
            f'{k}: {v}' for k, v in raw_res.headers.items()
        )
        response_head = f'{status_line}{response_header}{self.CRLF * 2}'
        response_body = raw_res.data
        self.log(response_head, 'RESP HEAD')
        self.log(response_body, 'RESP BODY')
        return self.encode(response_head) + response_body


    def dispatch(self, method, path, content=None, header={}):
        data_key = 'params' if method == 'GET' else 'data'
        content = dict(parse_qsl(content)) \
            if method == 'GET' else self.decode(content)
        return self._convert_bin_ret(
            getattr(requests, method.lower())(**{
                'url': f'{self.http_site}{path}',
                'stream': True,
                data_key: content
            })
        )


if __name__ == '__main__':
    payloads = [
        [
            ('GET', '/status/200'),
            ('GET', '/get', 'key=val&foo=bar'),
            ('POST', '/post', b'{"key": "value"}'),
            ('PUT', '/put', b'{"key": "value"}'),
            ('DELETE', '/delete'),
        ],
        [
            ('GET', '/image/png'),
            ('GET', '/image/jpeg'),
            ('GET', '/image/svg'),
        ]
    ]

    hp = HTTPProxy('https://httpbin.org')
    for argv in payloads[0]:
        print(hp.decode(hp.dispatch(*argv)))
    for argv in payloads[1]:
        print(hp.dispatch(*argv))
