import re
import socket
import select
from math import ceil
from urllib.parse import unquote
from importlib import import_module

from server.serpro import SerPro


class Server(SerPro):
    def __init__(self):
        super().__init__(self.__class__.__name__)


    def handle_request(self, request):
        method, path = request['method'], request['path']
        host = request['header']['Host']

        # Use host and path to determine which class should be instanced
        if host in self.http['upstream']:
            classname = 'HTTPProxy'
            self.log(
                f'Class {classname} Set For Host {host}',
                'CLASS NAME'
            )
        else:
            classname = self.serpro_default
            for regex, cname in self.serpro_class_map.items():
                if re.search(regex, path):
                    classname = cname
                    self.log(
                        f'Path {path}\n'
                        + f'Using Regex {regex}\n'
                        + f'Matched Class {cname}',
                        'CLASS NAME'
                    )
                    break

        # Check if the request method is valid
        mtd_stat_map = {
            'allow': 405,
            'impl': 501,
        }
        for mtd, stat in mtd_stat_map.items():
            if method not in self.methods[classname][mtd]:
                return self.http_resp(stat)

        # Import corresponding module and instanlize the class
        filename = self.class_file_map[classname]
        module = import_module(f'server.{filename}')
        instance = getattr(module, classname)()
        return instance.dispatch(**request)


    def interact(self, sock):
        # Parse HTTP request data with format defined in RFC
        # https://tools.ietf.org/html/rfc3986
        # https://tools.ietf.org/html/rfc2616#section-5
        sep = {
            # GET /path?val=key&foo=bar HTTP/1.1
            'reqline': ' ',

            # /path?val=key&foo=bar
            'query': '?',

            # Content-Type: text/html; charset=UTF-8
            # Left-trim to get value instead of using ': ' as sep
            'header': ':',
        }

        data = sock.recv(self.readbuf['first'])
        if not data:
            self.log(
                f'Received Empty Data From Client {sock}',
                'BAD REQUEST'
            )
            return self.http_resp(400)

        # This 'content' here may not be complete
        head, content = data.split(self.encode(self.CRLF * 2), 1)
        head = self.decode(head)
        self.log(head, 'REQ HEAD')

        # Parse the request line and string-dumped header
        reqline, strheader = head.split(self.CRLF, 1)
        method, path, _ = reqline.split(sep['reqline'], 2)
        path = unquote(path)

        # Parse query string from path if any
        query = ''
        if sep['query'] in path:
            path, query = path.split(sep['query'], 1)

        # Parse all header parameters
        header = {}
        for line in strheader.split(self.CRLF):
            key, val = line.split(sep['header'], 1)
            header[key] = val.lstrip()

        # All HTTP requests' header must contain 'Host'
        if not header or 'Host' not in header:
            self.log(
                f'Host Header Not Set For Client {sock}'
                'BAD REQUEST'
            )
            return self.http_resp(400)

        # Receive the rest of content according to 'Content-Length' header
        if self.conlen_key in header:
            conlen_tot = int(header[self.conlen_key])
            conlen_curr = len(content)
            while conlen_curr < conlen_tot:
                content += sock.recv(self.readbuf['left'])
                conlen_curr = len(content)

        # Note that type(content) is always bytes in this implementation
        if self.conlen_key in header:
            # 'Con-Len' is asserted to be equal with calculated conlen_val
            conlen_val = str(len(content))
            if header[self.conlen_key] != conlen_val:
                self.log(
                    f'Content-Length {header[self.conlen_key]} '
                    + f'And conlen_val {conlen_val} Failed To Match',
                    'INTERNAL ERROR'
                )
                return self.http_resp(500)
        elif content:
            # 'Con-Len' header should be set for request with entity-body
            # Actually there is an exception using the 'Transfer-Encoding' header
            # Which is not implemented here due to the complexity and lack of time
            # https://tools.ietf.org/html/rfc7230#section-3.3.2
            # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Transfer-Encoding
            self.log(
                f'Header {self.conlen_key} Not Set '
                + 'For Request With Entity Body'
                'NO CONLEN'
            )
            errcode = 501 if 'Transfer-Encoding' in header else 400
            return self.http_resp(errcode)

        # Generate and log the parsed request parameters
        request = {
            'method': method,
            'path': path,
            'query': query,
            'content': content,
            'header': header,
        }
        for key, val in request.items():
            self.log(
                f'{key.upper()}: {val}', 'REQUEST PARSE',
                self.logc['small'], False
            )
        return self.handle_request(request)


    def serve(self, host, port):
        # Bind to the configured host:port pair and start the server
        serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log(f'Starting Server {serversock} On {host}:{port}', 'SERVER INFO')
        serversock.bind((host, port))
        serversock.listen()

        # Register read event for server socket
        serverfd = serversock.fileno()
        evtmask = select.EPOLLIN
        epoll = select.epoll()
        epoll.register(serverfd, evtmask)
        fd_sock_map = {}

        while True:
            try:
                # Wait for new connections or client events
                fd_evt_list = epoll.poll()
            except BaseException:
                self.log(f'Closing Server {serversock}', 'SERVER INFO')
                serversock.close()
                exit(0)

            for fd, evt in fd_evt_list:
                if fd == serverfd:
                    # Server fd readable: accept new connection
                    sock, addr = serversock.accept()
                    self.log(f'Client {sock} Connection Accepted', 'CLIENT INFO')
                    fd_sock_map[sock.fileno()] = sock

                    # Register read event and prepare to receive request
                    epoll.register(sock, select.EPOLLIN)

                elif evt & select.EPOLLIN:
                    # Client data readable
                    sock = fd_sock_map[fd]
                    self.log(f'Client {sock} Data Readable', 'EPOLLIN')
                    response = self.interact(sock)

                    # Register write event and prepare to send response
                    epoll.modify(fd, select.EPOLLOUT)

                elif evt & select.EPOLLOUT:
                    # Client data writable
                    sock = fd_sock_map[fd]
                    self.log(f'Client {sock} Data Writable', 'EPOLLIN')
                    sock.send(response)

                    # Close connection with current client after data sent
                    self.log(f'Disconnecting Client {sock}', 'CLIENT INFO')
                    sock.close()

                    # Unregister events and delete from connection list
                    epoll.unregister(fd)
                    del fd_sock_map[fd]


if __name__ == '__main__':
    server = Server()
    server.serve(server.listen['host'], server.listen['port'])
