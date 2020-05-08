import re
import socket
import select

from sp import SP

class Server(SP):
    def __init__(self, proj_name='', bufsize=2048):
        super().__init__(proj_name=proj_name)
        self.bufsize = bufsize

    def bind_and_listen(self, host, port):
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
                exit(0)
            for fd, evt in fd_evt_list:
                if fd == ser_fd:
                    # Accept new connection
                    sock, addr = tcp_ser.accept()
                    epoll.register(sock, select.EPOLLIN)
                    fd_evt_map[sock.fileno()] = sock
                elif evt & select.EPOLLIN:
                    # Data readable
                    data = fd_evt_map[fd].recv(self.bufsize).decode(self.encoding)
                    status_ok = self.status_table['ok']
                    response = f'{self.http_version} {status_ok}{self.EOL}'
                    response += f'{self.server_info}{self.EOL}'
                    epoll.modify(fd, select.EPOLLOUT)
                elif evt & select.EPOLLOUT:
                    # Data writable
                    fd_evt_map[fd].send(response.encode(self.encoding))
                    fd_evt_map[fd].close()
                    epoll.unregister(fd)
                    del fd_evt_map[fd]
