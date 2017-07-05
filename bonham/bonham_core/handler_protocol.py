"""
/bonham/bonham_core/handler_protocol.py

Author: Tim "tjtimer" Jedro,
version. 0.0.1dev


"""
import os
import socket
import ssl
from _ssl import PROTOCOL_TLSv1_2

import asyncio

import arrow
from bonham.bonham_core.router import Router
from bonham.settings import SOCKET_FILE

__all__ = [
    'ssl_context',
    'get_sock_file',
    'prepared_socket',
    'ServiceProtocol'
    ]

ssl_context = ssl.SSLContext(protocol=PROTOCOL_TLSv1_2)
ssl_context.load_default_certs(purpose=ssl.Purpose.SERVER_AUTH)
ciphers = [cipher['description'] for cipher in ssl_context.get_ciphers() if 'TLSv1.2' in cipher['description']]
ssl_context.set_ciphers(ciphers[0])


def get_sock_file(_id):
    sock_file = f"{SOCKET_FILE}_{_id}.sock"
    if os.path.exists(sock_file):
        os.remove(sock_file)
    return sock_file


def prepared_socket(_id) -> ssl.SSLSocket:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    ssl_sock = ssl_context.wrap_socket(s)
    sock_file = f"{SOCKET_FILE}_{_id}.sock"
    if os.path.exists(sock_file):
        os.remove(sock_file)
    ssl_sock.bind(sock_file)
    os.chmod(sock_file, 666)
    ssl_sock.listen(100)
    return ssl_sock


def validate(headers):
    print(headers)


def create_response_headers(received_headers: bytes)->bytes:
    now = bytes(arrow.now().replace(minutes=-10).for_json(), encoding='utf-8')
    headers = dict(
            status_line=b'HTTP/1.1 200 OK',
            charset=b'charset: utf-8',
            location=b'Location: /',
            transfer_encoding=b'Transfer-Encoding: gzip, deflate, chunked, compress',
            x_xss_protection=b'X-XSS-Protection: True',
            strict_transport_securitiy=b'Strict-Transport-Security: max-age=31536000\r\n'
                             b'Strict-Transport-Security: max-age=31536000; includeSubDomains\r\n'
                             b'Strict-Transport-Security: max-age=31536000; preload',
            date=b'Date: ' + now,
            keep_alive=b'Keep-Alive: timeout=5, max=1000',
            last_modified=b'Last-Modified: ' + now
            )
    byte_headers = b'\r\n'.join(headers.values())
    print('response headers', byte_headers)
    return byte_headers


class ServiceProtocol(asyncio.Protocol):
    def __init__(self):
        print('protocol initialized')
        self.transport = None
        self.data_sent = []

    def connection_made(self, transport):
        print(f"connection made")
        self.transport = transport
        self.transport.get_extra_info('peername')

    def data_received(self, data):
        print('data received', data)
        chunks = data.decode().split('\n\n')
        received = ''.join(chunks)
        response_headers = create_response_headers(received)
        response_headers += b'\r\nContent-Length: ' + bytes(str(len(b'\r\n\r\nYEAH!;')), encoding='utf-8')
        response_content = b''.join([response_headers, b'\r\n\r\nYEAH!' ])
        self.transport.write(response_content)
        return self.data_sent.append(response_content)

    def eof_received(self):
        print('eof received ')
        print(vars(self))

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, *args, **kwargs):
        print('connection lost: ', vars(self))
        self.shutdown()

    def shutdown(self):
        self.transport.close()
