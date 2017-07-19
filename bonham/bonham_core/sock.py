import os
import socket
import ssl
from _ssl import PROTOCOL_TLSv1_2

from bonham.settings import APPLICATION_NAME, SOCK_DIR

__all__ = (
    'get_ssl_context',
    'create_ssl_socket'
    )


def get_ssl_context(*,
                    protocol=PROTOCOL_TLSv1_2,
                    purpose=ssl.Purpose.SERVER_AUTH, **kwargs) -> ssl.SSLContext:
    ssl_context = ssl.SSLContext(protocol=protocol)
    ssl_context.load_default_certs(purpose=purpose)
    default_ciphers_list = [
        cipher['description'] for cipher in ssl_context.get_ciphers() if 'TLSv1.2' in cipher['description']
        ]
    default_ciphers = default_ciphers_list[0]
    ssl_context.set_ciphers(kwargs.pop('ciphers', default_ciphers))
    return ssl_context


def create_ssl_socket(_id, **kwargs) -> ssl.SSLSocket:
    sock_path = os.path.join(SOCK_DIR, f"{APPLICATION_NAME}_{_id}.sock")
    if os.path.exists(sock_path):
        os.remove(sock_path)
    ssl_context = get_ssl_context()
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    ssl_sock = ssl_context.wrap_socket(s)
    ssl_sock.bind(sock_path)
    os.chmod(sock_path, 666)
    ssl_sock.listen(kwargs.pop('listen', 100))
    print(sock_path, ssl_sock)
    return ssl_sock
