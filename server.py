import re
import socket
import select

tcp_ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_ser.bind(('', 80))
tcp_ser.listen()
tcp_ser.setblocking(False)
ser_fd = tcp_ser.fileno()
epoll = select.epoll()
epoll.register(ser_fd, select.EPOLLIN)
fd_evt_map = {}

while True:
    try:
        fd_evt_list = epoll.poll()
    except BaseException:
        print('Server Closing...')
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
            client = fd_evt_map[fd]
            data = client.recv(2048).decode('utf-8')
            print(data)
            response = 'HTTP/1.1 200 OK\r\n'.encode('utf-8')
            epoll.modify(fd, select.EPOLLOUT)
        elif evt & select.EPOLLOUT:
            # Data writable
            client.send(response)
            client.close()
            epoll.unregister(fd)
            del fd_evt_map[fd]
