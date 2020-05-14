import requests
import requests.exceptions as rerr
from urllib.parse import parse_qsl

from server.serpro import SerPro
from server.mocker import mock_request


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
        self.log(response_head, 'RESP HEAD')

        # Note: the content of res.content is the same as raw_res.data
        # But the latter should not be used even with stream=True set
        # To prevent raising uncaught urllib3.exceptions.ReadTimeoutError
        response_body = res.content
        self.log(response_body, 'RESP BODY', self.logc['large'])
        return self.encode(response_head) + response_body


    def dispatch(self, method, path, query, content, header):
        try:
            upstream = self.http['upstream'][header['Host']]
        except KeyError:
            self.log('HTTP Upstream Not Found, Default Selected', 'UPSTREAM')
            upstream = self.http['upstream']['default']

        try:
            http_ret = self._convert_res(
                # https://github.com/psf/requests/blob/master/requests/api.py
                getattr(requests, method.lower())(**{
                    'url': upstream + path,
                    'headers': header if self.http['header'] else {},
                    'params': dict(parse_qsl(query)),
                    'data': content,
                    'timeout': self.http['timeout'],
                    'stream': True,
                })
            )
        except rerr.Timeout:
            return self.http_resp(504)
        except rerr.RequestException:
            return self.http_resp(502)
        return http_ret


if __name__ == '__main__':
    payloads = {
        'text': [
            ['GET', '/status/200'],
            ['GET', '/get', 'key=val&foo=bar'],
            ['POST', '/post', '', {"key": "value"}, {'X-Mock': 'http proxy'}],
            ['PUT', '/put', '', b'requests mock'],
            ['DELETE', '/delete'],
        ],
        'raw': [
            ['GET', '/image/png'],
            ['GET', '/image/jpeg'],
            ['GET', '/image/svg'],
        ],
    }
    mock_request(payloads, HTTPProxy())
