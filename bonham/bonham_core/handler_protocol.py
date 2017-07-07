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
import httptools

from bonham.bonham_core.router import Router
from bonham.bonham_core.templates import Template
from bonham.bonham_protocols.request_parser_protocol import RequestParserProtocol
from bonham.settings import SOCKET_FILE, TEMPLATES_DIR

__all__ = [
    'ssl_context',
    'get_socket_file',
    'prepared_socket',
    'ServiceProtocol'
    ]


def get_ssl_context(*,
                    protocol=PROTOCOL_TLSv1_2,
                    purpose=ssl.Purpose.SERVER_AUTH, **kwargs):
    ssl_context = ssl.SSLContext(protocol=protocol)
    ssl_context.load_default_certs(purpose=purpose)
    default_ciphers = [
        cipher['description'] for cipher in ssl_context.get_ciphers() if 'TLSv1.2' in cipher['description']
        ][0]
    ssl_context.set_ciphers(('ciphers', default_ciphers))
    return ssl_context


def get_socket_file(_id):
    sock_file = f"{SOCKET_FILE}_{_id}.sock"
    if os.path.exists(sock_file):
        os.remove(sock_file)
    return sock_file  # will be created on my_socket.bind() method.


def create_ssl_socket(_id, **kwargs) -> ssl.SSLSocket:
    sock_file = get_socket_file(_id)
    ssl_context = get_ssl_context()
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    ssl_sock = ssl_context.wrap_socket(s)
    ssl_sock.bind(sock_file)
    ssl_sock.listen(kwargs.pop('listen', 100))
    return ssl_sock


def validate(headers):
    print(headers)


def create_response_headers(received_headers: bytes)->bytes:
    now = bytes(arrow.now().replace(minutes=-10).for_json(), encoding='utf-8')
    headers = dict(
            status_line=b'HTTP/1.1 200 OK',
            charset=b'charset: utf-8',
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


class ServiceProtocol(asyncio.DatagramProtocol):
    def __init__(self):
        print('protocol initialized')
        self.loop = asyncio.get_event_loop()
        self.transport = None
        self.request_parser = httptools.HttpRequestParser(RequestParserProtocol)
        # self.response_parser = httptools.HttpResponseParser()
        self.http_version = 'HTTP/1.1'
        self.method = b'GET'
        self.keep_alive = False
        self.response = b'pong'

    def connection_made(self, transport):
        print(f"connection made")
        self.transport = transport
        self.http_version = self.request_parser.get_http_version()
        self.method = self.request_parser.get_method()
        self.keep_alive = self.request_parser.should_keep_alive()

    def data_received(self, data, addr):
        print('data received', data, addr)
        self.request_parser.feed_data(data)

    def eof_received(self):
        print('eof received ')

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, *args, **kwargs):
        print('connection lost: ', vars(self))
        self.shutdown()

    def pause_writing(self):
        print("pause writing")

    def resume_writing(self):
        print('resume writing')

    def shutdown(self):
        self.transport.close()
