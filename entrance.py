import re
import socket
import select
from importlib import import_module

from log.log import Log
from server.sp import SP


class Entrance(SP):
    def __init__(self):
        super().__init__()
        self.log = Log('Entrance', self.conf['logfile']).append


    def handle_request(self, data, filedata):
        # REF: https://www.w3.org/Protocols/rfc2616/rfc2616-sec5.html
        sep = {
            'get': '?',
            'line': ' ',
            'header': ':',
            'linehead': self.CRLF,
            'headbody': self.CRLF * 2,
        }
        # Type of `content`: `query_string` for GET method and `bytes` otherwise
        head, content = data.split(self.encode(sep['headbody']), 1)
        if filedata:
            self.log(
                'File Upload Detected, Sending To Upstream...',
                'FILE UPLOAD'
            )
            content = filedata
        head = self.decode(head)
        self.log(head, 'REQ HEAD')
        reqline, sheader = head.split(sep['linehead'], 1)
        method, path, _ = reqline.split(sep['line'], 2)
        if sep['get'] in path:
            path, content = path.split(sep['get'], 1)
        header = {}
        for line in sheader.split(self.CRLF):
            name, value = line.split(sep['header'], 1)
            value = value.lstrip()
            header[name] = value

        classname = self.conf['serpro_default']
        for regex, cname in self.conf['serpro_class_map'].items():
            if re.search(regex, path):
                classname = cname
                self.log(
                    f'Path `{path}`\nUsing Regex `{regex}`\nMatched Class `{cname}`',
                    'CLASS NAME'
                )
                path = re.split(regex, path)[1] \
                    if cname == 'HTTPProxy' else path
                break
        filename = self.conf['class_file_map'][classname]
        module = import_module(f'server.{filename}')
        instance = getattr(module, classname)(**{
            'root_dir': self.conf['docroot'],
            'proj_name': self.conf['project'],
            'index_file': self.conf['idxfile'],
            'sock_dir': self.conf['sockfile'],
            'http_site': self.conf['http_proxy_site']
        })
        kwargs = {
            'method': method,
            'path': path,
            'content': content,
            'header': header
        }
        self.log(kwargs, 'SERVER DISPATCH')
        return instance.dispatch(**kwargs)


    def serve(self, host, port):
        self.log(f'Starting Server On {host}:{port}', 'SERVER INFO')
        tcp_ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_ser.bind((host, port))
        tcp_ser.listen()
        ser_fd = tcp_ser.fileno()
        epoll = select.epoll()
        epoll.register(ser_fd, select.EPOLLIN)
        fd_evt_map = {}
        while True:
            try:
                fd_evt_list = epoll.poll()
            except BaseException:
                tcp_ser.close()
                self.log(f'Server Closed', 'SERVER INFO')
                exit(0)
            for fd, evt in fd_evt_list:
                if fd == ser_fd:
                    # Accept new connection
                    sock, addr = tcp_ser.accept()
                    self.log(
                        f'Client `{sock}` Accepted', 'CLIENT INFO'
                    )
                    epoll.register(sock, select.EPOLLIN)
                    fd_evt_map[sock.fileno()] = sock
                elif evt & select.EPOLLIN:
                    # Data readable
                    client = fd_evt_map[fd]
                    data = client.recv(self.bufsize)
                    if data:
                        self.log(
                            f'Recv Data From Client:\n{data}', 'EPOLLIN'
                        )
                        filedata = client.recv(self.bufsize) \
                            if b'multipart/form-data' in data else None
                        response = self.handle_request(data, filedata)
                        epoll.modify(fd, select.EPOLLOUT)
                elif evt & select.EPOLLOUT:
                    # Data writable
                    self.log(
                        f'Write Data To Client:\n{response}', 'EPOLLOUT'
                    )
                    fd_evt_map[fd].send(response)
                    self.log(
                        f'Disconnecting Client `{fd_evt_map[fd]}`', 'CLIENT INFO'
                    )
                    fd_evt_map[fd].close()
                    epoll.unregister(fd)
                    del fd_evt_map[fd]


if __name__ == '__main__':
    entrance = Entrance()
    entrance.serve(
        entrance.conf['host'],
        entrance.conf['port']
    )
