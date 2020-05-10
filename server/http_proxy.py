import requests
import requests.exceptions as rerr
from urllib.parse import parse_qsl

from server.serpro import SerPro


class HTTPProxy(SerPro):
    def __init__(self):
        super().__init__(self.__class__.__name__)


    def _convert_res(self, res):
        raw_res = res.raw
        status_line = f'HTTP/{raw_res.version // 10}.{raw_res.version % 10} '
        status_line += f'{raw_res.status} {raw_res.reason}{self.CRLF}'
        response_header = self.CRLF.join(
            f'{key}: {val}' for key, val in raw_res.headers.items()
        )
        response_head = f'{status_line}{response_header}{self.CRLF * 2}'
        response_body = raw_res.data
        self.log(response_head, 'RESP HEAD')
        self.log(response_body, 'RESP BODY', self.logc['large'])
        return self.encode(response_head) + response_body


    def dispatch(self, method, path, content, header):
        upstream = self.http['upstream'][header['Host']]
        data_key = 'params' if method == 'GET' else 'data'
        content = dict(parse_qsl(content)) \
            if method == 'GET' else self.decode(content)

        try:
            http_ret = self._convert_res(
                getattr(requests, method.lower())(**{
                    'url': upstream + path,
                    'timeout': self.http['timeout'],
                    'stream': True,
                    data_key: content,
                })
            )
        except rerr.Timeout:
            return self.http_resp(504)
        except rerr.RequestException:
            return self.http_resp(502)
        return http_ret


if __name__ == '__main__':
    payloads = [
        [
            ('GET', '/status/200', '', {}),
            ('GET', '/get', 'key=val&foo=bar', {}),
            ('POST', '/post', b'{"key": "value"}', {}),
            ('PUT', '/put', b'{"key": "value"}', {}),
            ('DELETE', '/delete', '', {}),
        ],
        [
            ('GET', '/image/png', '', {}),
            ('GET', '/image/jpeg', '', {}),
            ('GET', '/image/svg', '', {}),
        ],
    ]

    hp = HTTPProxy()
    for argv in payloads[0]:
        print(hp.decode(hp.dispatch(*argv)))
    for argv in payloads[1]:
        print(hp.dispatch(*argv))
