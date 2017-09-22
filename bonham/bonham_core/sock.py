import logging
import socket
import ssl
from _ssl import PROTOCOL_TLSv1_2

__all__ = (
    'get_ssl_context',
    'create_ssl_socket'
    )

log = logging.getLogger(__name__)


def get_ssl_context(*,
                    protocol=PROTOCOL_TLSv1_2,
                    purpose=ssl.Purpose.CLIENT_AUTH,
                    **kwargs) -> ssl.SSLContext:
    ssl_context = ssl.SSLContext(protocol=protocol)
    ssl_context.load_default_certs(purpose=purpose)
    default_ciphers_list = [
        cipher['description'] for cipher in ssl_context.get_ciphers() if 'TLSv1.2' in cipher['description']
        ]
    default_ciphers = default_ciphers_list[0]
    ssl_context.set_ciphers(kwargs.pop('ciphers', default_ciphers))
    return ssl_context


def create_ssl_socket(address, **kwargs) -> ssl.SSLSocket:
    print(address)
    ssl_context = get_ssl_context()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, True)
    except (AttributeError, OSError) as e:
        log.warning('reuse_port=True option failed', exc_info=True)
    s.setblocking(0)
    ssl_sock = ssl_context.wrap_socket(s)
    ssl_sock.bind(address)
    ssl_sock.listen(kwargs.pop('listen', 100))
    return ssl_sock
