#!/usr/bin/python3

import os
import errno
import socket
import logging
from handler import Handler
from optparse import OptionParser


def read_all(socket_received, max_buff, TIMEOUT=5):
    data_received = b''
    socket_received.settimeout(TIMEOUT)
    while True:
        buffer = socket_received.recv(max_buff)
        data_received += buffer
        if not buffer or b'\r\n\r\n' in data_received:
            break
    return data_received


def run(server_address, server_port, root_directory, worker_num, max_buff):
    worker_process = []
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((server_address, server_port))
    server_sock.listen()

    for i in range(worker_num):
        process_id = os.fork()
        if process_id != 0:
            worker_process.append(process_id)
        else:
            while True:
                try:
                    client_sock, address = server_sock.accept()
                except IOError as e:
                    if e.errno == errno.EINTR:
                        continue
                    raise
                request_data = read_all(client_sock, max_buff)
                if len(request_data.strip()) == 0:
                    client_sock.close()
                    continue
                handler_process = Handler(request_data, root_directory)
                if request_data:
                    response_data = handler_process.generate_response(request_data.decode())
                    client_sock.sendall(response_data)
                client_sock.close()
    server_sock.close()

    for current_pid in worker_process:
        os.waitpid(current_pid, 0)


if __name__ == '__main__':
    op = OptionParser()
    op.add_option("-p", "--port", type=int, default=80)
    op.add_option("-r", "--root", type=str, default='/')
    op.add_option("-w", "--worker", type=int, default=1)
    op.add_option("-b", "--buffer", type=int, default=1024)
    (opts, args) = op.parse_args()
    DOCUMENT_ROOT = opts.root if opts.root.startswith('/') else '/' + opts.root
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    logging.info('Starting server at %s' % opts.port)
    logging.info('DOCUMENT_ROOT is %s' % DOCUMENT_ROOT)
    run('127.0.0.1', opts.port, DOCUMENT_ROOT, opts.worker, opts.buffer)



