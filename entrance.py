import re
import socket
import select
from math import ceil
from importlib import import_module

from server.serpro import SerPro


class Entrance(SerPro):
    def __init__(self):
        super().__init__(self.__class__.__name__)


    def handle_request(self, request):
        method, path = request['method'], request['path']

        # Use `path` to determine which class to be instanced
        classname = self.serpro_default
        for regex, cname in self.serpro_class_map.items():
            if re.search(regex, path):
                classname = cname
                self.log(
                    f'Path `{path}`\nUsing Regex `{regex}`\nMatched Class `{cname}`',
                    'CLASS NAME'
                )
                path = re.split(regex, path)[1] \
                    if cname == 'HTTPProxy' else path
                break

        # Check if the request method is valid
        mtd_stat_map = {
            'allow': 405,
            'impl': 501,
        }
        for mtd, stat in mtd_stat_map.items():
            if method not in self.methods[classname][mtd]:
                return self.encode(self.http_resp(stat))

        # Import corresponding module and instanlize the class
        filename = self.class_file_map[classname]
        module = import_module(f'server.{filename}')
        instance = getattr(module, classname)()
        return instance.dispatch(**request)


    def interact(self, sock):
        # REF: https://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html
        sep = {
            # /path?val=key&foo=bar
            'qstring': '?',

            # GET /path HTTP/1.1
            'reqline': ' ',

            # Content-Type: text/html; charset=UTF-8
            # Left-trim to get value instead of using ': ' as sep
            'header': ':',
        }

        data = sock.recv(self.readbuf['first'])
        if not data:
            return self.encode(self.http_resp(400))

        # This `content` here may not be completed
        head, content = data.split(self.encode(self.CRLF * 2), 1)
        head = self.decode(head)
        self.log(head, 'REQ HEAD')

        # Parse the request line and string-dumped header
        reqline, strheader = head.split(self.CRLF, 1)
        method, path, _ = reqline.split(sep['reqline'], 2)

        # Parse query_string from path if any
        if sep['qstring'] in path:
            path, content = path.split(sep['qstring'], 1)

        # Parse all header parameters
        header = {}
        for line in strheader.split(self.CRLF):
            key, val = line.split(sep['header'], 1)
            header[key] = val.lstrip()

        # Receive the rest of content according to 'Content-Length' header
        if self.conlen_key in header:
            conlen_val = header[self.conlen_key]
            conlen_tot = int(conlen_val)
            conlen_curr = len(content)
            if conlen_curr < conlen_tot:
                # Calculate the frequency to read according to buffer size in config
                bufsize = self.readbuf['left']
                freq = ceil((conlen_tot - conlen_curr) / bufsize)
                self.log(
                    'Appending content while reading left message body\n'
                    + f'CURR {conlen_curr} / TOT {conlen_tot} '
                    + f'/ BUF {bufsize} / FREQ {freq}',
                    'REQ RECV'
                )
                for _ in range(freq):
                    content += sock.recv(bufsize)

        # Type of `content`: query_string if any and bytes otherwise
        conlen_tot = len(content)
        conlen_val = str(conlen_tot)

        if self.conlen_key in header:
            # 'Con-Len' is asserted to be equal with calculated conlen_val
            if header[self.conlen_key] != conlen_val:
                self.log(
                    f'Content-Length {header[self.conlen_key]} '
                    + f'and conlen_val {conlen_val} failed to match',
                    'INTERNAL ERROR'
                )
                return self.encode(self.http_resp(500))
        elif type(content) is bytes:
            # 'Con-Len' header should be set for bytes content
            missed_val = f'"{self.conlen_key}: {conlen_val}"'
            self.log(
                f'Set the missed {missed_val} for bytes content',
                'CONLEN SET'
            )
            header[self.conlen_key] = conlen_val

        # Generate and log the parsed request parameters
        request = {
            'method': method,
            'path': path,
            'content': content,
            'header': header,
        }
        for key, val in request.items():
            self.log(
                f'{key.upper()}: {val}', 'REQUEST PARSE',
                self.logc['coth'], False
            )
        return self.handle_request(request)


    def serve(self, host, port):
        # Bind to the configured host:port pair and start the server
        serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log(f'Starting Server `{serversock}` On {host}:{port}', 'SERVER INFO')
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
                self.log(f'Closing Server `{serversock}`', 'SERVER INFO')
                serversock.close()
                exit(0)

            for fd, evt in fd_evt_list:
                if fd == serverfd:
                    # Server fd readable: accept new connection
                    sock, addr = serversock.accept()
                    self.log(f'Client `{sock}` Connection Accepted', 'CLIENT INFO')
                    fd_sock_map[sock.fileno()] = sock

                    # Register read event and prepare to receive request
                    epoll.register(sock, select.EPOLLIN)

                elif evt & select.EPOLLIN:
                    # Client data readable
                    sock = fd_sock_map[fd]
                    self.log(f'Client `{sock}` Data Readable', 'EPOLLIN')
                    response = self.interact(sock)

                    # Register write event and prepare to send response
                    epoll.modify(fd, select.EPOLLOUT)

                elif evt & select.EPOLLOUT:
                    # Client data writable
                    sock = fd_sock_map[fd]
                    self.log(f'Client `{sock}` Data Writable', 'EPOLLIN')
                    sock.send(response)

                    # Close connection with current client after data sent
                    self.log(f'Disconnecting Client `{sock}`', 'CLIENT INFO')
                    sock.close()

                    # Unregister events and delete from connection list
                    epoll.unregister(fd)
                    del fd_sock_map[fd]


if __name__ == '__main__':
    server = Entrance()
    server.serve(server.listen['host'], server.listen['port'])
